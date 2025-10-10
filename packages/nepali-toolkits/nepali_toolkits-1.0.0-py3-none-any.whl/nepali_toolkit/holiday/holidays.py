# src/nepali_toolkit/bs/holidays.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Optional, Sequence, Dict, List, Tuple
import re

from nepali_toolkit.common.util import read_json_resource
from nepali_toolkit.exceptions import ValidationError

from nepali_toolkit.bs.calendar import BSCalendar



_BS_DATE_RE = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")


def _parse_bs_tuple(bs: str) -> Tuple[int, int, int]:
    """Parse 'YYYY-MM-DD' into (y, m, d). Raise ValidationError if malformed."""
    m = _BS_DATE_RE.match(bs)
    if not m:
        raise ValidationError(f"BS date must be 'YYYY-MM-DD', got: {bs!r}")
    y, mo, d = map(int, m.groups())
    if not (1 <= mo <= 12):
        raise ValidationError(f"BS month out of range in {bs!r}")
    if not (1 <= d <= 32):
        # 32 is a safe upper bound before validating by month-length table (not needed here)
        raise ValidationError(f"BS day out of range in {bs!r}")
    return y, mo, d


def _norm_tags(tags: Optional[Iterable[str]]) -> List[str]:
    return sorted({t.strip().lower() for t in (tags or []) if t and t.strip()})


@dataclass(frozen=True)
class HolidayRecord:
    """One holiday entry normalized from JSON."""
    bs: str
    ad: Optional[str]
    name_en: str
    name_ne: str
    tags: List[str]  # lowercase

    @staticmethod
    def from_json(obj: Dict) -> "HolidayRecord":
        # Skip "section" rows (used only for display/structure)
        if "section" in obj:
            raise ValueError("section rows are not HolidayRecord entries")

        bs = obj.get("bs")
        if not bs:
            raise ValidationError("Holiday item missing 'bs' date")

        # Validate and normalize
        y, m, d = _parse_bs_tuple(str(bs))
        bs_norm = f"{y:04d}-{m:02d}-{d:02d}"

        name_en = str(obj.get("name_en", "")).strip()
        name_ne = str(obj.get("name_ne", "")).strip()

        # 'ad' is optional. Keep as ISO string if present, else None.
        ad = obj.get("ad")
        if ad is not None:
            ad = str(ad).strip()
            # basic sanity check (not strict parse; you can tighten if needed)
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", ad):
                ad = None

        tags = _norm_tags(obj.get("tags"))
        return HolidayRecord(bs=bs_norm, ad=ad, name_en=name_en, name_ne=name_ne, tags=tags)

    @property
    def bs_tuple(self) -> Tuple[int, int, int]:
        return _parse_bs_tuple(self.bs)

    def to_dict(self) -> Dict:
        return {
            "bs": self.bs,
            "ad": self.ad,
            "name_en": self.name_en,
            "name_ne": self.name_ne,
            "tags": list(self.tags),
        }


class Holidays:

    def __init__(
        self,
        dataset_package: str = "nepali_toolkit.bs.data",
        filenames: Sequence[str] = ("holidays_bs_2082.json",),
        calendar: Optional["BSCalendar"] = None,
    ) -> None:
        self._calendar = calendar
        self._years: Dict[int, List[HolidayRecord]] = {}
        self._load_many(dataset_package, filenames)
        self._index_cache: Dict[int, Dict[Tuple[int, int, int], HolidayRecord]] = {}



    def _load_many(self, pkg: str, files: Sequence[str]) -> None:
        merged: Dict[int, List[HolidayRecord]] = {}
        for fname in files:
            data = read_json_resource(pkg, fname)
            years = data.get("years", {})
            if not isinstance(years, dict):
                continue
            for y_str, items in years.items():
                try:
                    year = int(y_str)
                except Exception:
                    continue
                if not isinstance(items, list):
                    continue
                bucket = merged.setdefault(year, [])
                for raw in items:
                    if not isinstance(raw, dict):
                        continue
                    if "section" in raw:
                        continue
                    try:
                        rec = HolidayRecord.from_json(raw)
                        if rec.ad is None and self._calendar is not None:
                            try:
                                ad_date = self._calendar.to_ad(rec.bs)
                                object.__setattr__(rec, "ad", ad_date.isoformat())
                            except Exception:
                                pass
                        bucket.append(rec)
                    except Exception:
                        continue

        for y, arr in merged.items():
            arr.sort(key=lambda r: r.bs_tuple)
        self._years = merged


    def list_years(self) -> List[int]:
        return sorted(self._years.keys())
    
    def _current_bs_year(self) -> int:
        if self._calendar is not None:
            try:
                return self._calendar.today_bs().year
            except Exception:
                pass
        if self._years:
            return max(self._years.keys())
        raise ValidationError("No holiday data loaded; cannot infer current BS year.")
    
    def _row_matches_query(self, row: Dict, needle: str) -> bool:
        n = needle.casefold()
        return (
            (row.get("name_en", "") or "").casefold().find(n) >= 0
            or (row.get("name_ne", "") or "").casefold().find(n) >= 0
            or (row.get("bs", "")      or "").casefold().find(n) >= 0
            or (row.get("ad", "")      or "").casefold().find(n) >= 0
        )

    def list_holiday(
        self,
        year: Optional[int] = None,
        *,
        query: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
        month: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:

        if year is None:
            year = self._current_bs_year()

        if year not in self._years:
            raise ValidationError(f"Year {year} not available in the loaded holiday dataset.")

        records = list(self._years.get(year, []))

        if tags:
            tags_set = {t.strip().lower() for t in tags if t and t.strip()}
            if tags_set:
                records = [r for r in records if tags_set.issubset(set(r.tags))]

        if month is not None:
            if not (1 <= month <= 12):
                raise ValidationError("month must be between 1 and 12")
            records = [r for r in records if r.bs_tuple[1] == month]

        rows = [r.to_dict() for r in records]

    # Text query (case-insensitive substring in name_en/name_ne/bs/ad)
        if query:
            q = query.strip()
            if q:
                rows = [row for row in rows if self._row_matches_query(row, q)]

        # Limit
        if limit is not None:
            if limit < 0:
                return []
            rows = rows[:limit]

        return rows
    

    def is_holiday(
        self,
        bs_date: str,
        *,
        tags: Optional[Iterable[str]] = None,
    ) -> Tuple[bool, Optional[Dict]]:

        y, m, d = _parse_bs_tuple(bs_date)
        rec = self._index_get(y).get((y, m, d))
        if not rec:
            return False, None
        if tags:
            tags_set = {t.strip().lower() for t in tags if t and t.strip()}
            if not tags_set.issubset(set(rec.tags)):
                return False, None
        return True, rec.to_dict()

    def next_holiday(
        self,
        bs_from: str,
        *,
        limit: int = 5,
        tags: Optional[Iterable[str]] = None,
        inclusive: bool = False,
    ) -> List[Dict]:

        y, m, d = _parse_bs_tuple(bs_from)
        tags_set = {t.strip().lower() for t in (tags or []) if t and t.strip()} or None
        want = []

        def _push_year(year: int, start_tuple: Optional[Tuple[int, int, int]]) -> None:
            arr = self._years.get(year, [])
            for r in arr:
                if tags_set and not tags_set.issubset(set(r.tags)):
                    continue
                if start_tuple:
                    if inclusive:
                        if r.bs_tuple < start_tuple:
                            continue
                    else:
                        if r.bs_tuple <= start_tuple:
                            continue
                want.append(r)
                if len(want) >= limit:
                    return

        _push_year(y, (y, m, d))
        if len(want) < limit:
            next_years = [yy for yy in self.list_years() if yy > y]
            for yy in next_years:
                _push_year(yy, None)
                if len(want) >= limit:
                    break

        return [r.to_dict() for r in want[:limit]]

    def list_holiday_between(
        self,
        bs_start: str,
        bs_end: str,
        *,
        tags: Optional[Iterable[str]] = None,
    ) -> List[Dict]:

        y1, m1, d1 = _parse_bs_tuple(bs_start)
        y2, m2, d2 = _parse_bs_tuple(bs_end)
        if (y2, m2, d2) < (y1, m1, d1):
            raise ValidationError("bs_end must be >= bs_start")

        tags_set = {t.strip().lower() for t in (tags or []) if t and t.strip()} or None
        out: List[HolidayRecord] = []

        for y in self.list_years():
            if y < y1 or y > y2:
                continue
            for r in self._years.get(y, []):
                if tags_set and not tags_set.issubset(set(r.tags)):
                    continue
                if (y1, m1, d1) <= r.bs_tuple <= (y2, m2, d2):
                    out.append(r)
        out.sort(key=lambda r: r.bs_tuple)
        return [r.to_dict() for r in out]


    def _index_get(self, year: int) -> Dict[Tuple[int, int, int], HolidayRecord]:
        idx = self._index_cache.get(year)
        if idx is not None:
            return idx
        idx = {}
        for r in self._years.get(year, []):
            idx[r.bs_tuple] = r
        self._index_cache[year] = idx
        return idx
