# src/nepali_toolkit/holiday/__init__.py
from __future__ import annotations

from typing import Iterable, Optional, Sequence, List, Dict

from nepali_toolkit.bs.calendar import BSCalendar
from nepali_toolkit.holiday.holidays import Holidays  # <-- use the service class

__all__ = [
    "list_holiday",
    "next_holiday",
    "list_holiday_between",
]

# -------- internal singletons (lazy) --------
_cal: Optional[BSCalendar] = None
_srv: Optional[Holidays] = None  # <-- correct type

_default_tz = "Asia/Kathmandu"
_default_pkg = "nepali_toolkit.bs.data"
_default_files: Sequence[str] = ("holidays_bs_2082.json",)

def configure(
    *,
    tz: str = "Asia/Kathmandu",
    dataset_package: str = _default_pkg,
    filenames: Sequence[str] = _default_files,
) -> None:
    """
    Configure the shared holiday service.

    tz: IANA timezone used to infer current BS year when 'year' is omitted.
    dataset_package: package containing holiday JSON files.
    filenames: one or more holiday JSON files to load & merge.
    """
    global _cal, _srv, _default_tz, _default_pkg, _default_files
    _default_tz = tz
    _default_pkg = dataset_package
    _default_files = filenames
    _cal = BSCalendar(tz)
    _srv = Holidays(dataset_package=dataset_package, filenames=filenames, calendar=_cal)  # <-- instantiate Holidays

def _service() -> Holidays:
    """Return the shared Holidays instance, auto-configured if needed."""
    global _cal, _srv
    if _cal is None:
        _cal = BSCalendar(_default_tz)
    if _srv is None:
        _srv = Holidays(dataset_package=_default_pkg, filenames=_default_files, calendar=_cal)  # <-- instantiate Holidays
    return _srv

# ============== Public function API (only these three) ==============

def list_holiday(
    year: Optional[int] = None,
    *,
    query: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    month: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[Dict]:
    """List holidays in a BS year (defaults to current BS year in configured TZ)."""
    return _service().list_holiday(year, query=query, tags=tags, month=month, limit=limit)

def next_holiday(
    bs_from: str,
    *,
    limit: int = 5,
    tags: Optional[Iterable[str]] = None,
    inclusive: bool = False,
) -> List[Dict]:
    """Next upcoming holidays from a BS date."""
    return _service().next_holiday(bs_from, limit=limit, tags=tags, inclusive=inclusive)

def list_holiday_between(
    bs_start: str,
    bs_end: str,
    *,
    tags: Optional[Iterable[str]] = None,
) -> List[Dict]:
    """Holidays between two BS dates (inclusive)."""
    return _service().list_holiday_between(bs_start, bs_end, tags=tags)
