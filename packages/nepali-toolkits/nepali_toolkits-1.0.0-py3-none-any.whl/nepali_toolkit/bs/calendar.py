# nepali_toolkit/bs/calendar.py
from __future__ import annotations

from datetime import date as _date, datetime, timedelta
from typing import overload, Tuple
from dateutil.parser import isoparse
import pytz

from .types import BSDate
from .dataset import load_month_table
from nepali_toolkit.exceptions import OutOfRangeError, ValidationError
from nepali_toolkit.common.i18n import (
    BS_MONTHS_EN, BS_MONTHS_NE,
    AD_MONTHS_EN, AD_MONTHS_NE,
    to_ne_digits,
)

Lang = str


class BSCalendar:
    def __init__(self, tz: str = "Asia/Kathmandu"):
        self.tz = tz
        tbl = load_month_table()
        self._years: dict[str, list[int]] = tbl["years"]
        self._anchor_bs = self._parse_bs(tbl["anchor"]["bs"])
        self._anchor_ad = self._parse_ad(tbl["anchor"]["ad"])

    # -----------------------
    # Parsing helpers
    # -----------------------
    @staticmethod
    def _parse_ad(d) -> _date:
        return d if isinstance(d, _date) else isoparse(str(d)).date()

    @staticmethod
    def _parse_bs(s) -> BSDate:
        if isinstance(s, BSDate):
            return s
        parts = str(s).split("-")
        if len(parts) != 3:
            raise ValidationError("BS date must be YYYY-MM-DD")
        y, m, d = map(int, parts)
        return BSDate(y, m, d)

    def _validate_bs(self, t: BSDate) -> None:
        ys = str(t.year)
        if ys not in self._years:
            raise OutOfRangeError(f"BS year {t.year} outside coverage.")
        if not (1 <= t.month <= 12):
            raise ValidationError("BS month out of range (1..12)")
        dim = self._years[ys][t.month - 1]
        if not (1 <= t.day <= dim):
            raise ValidationError(f"BS day out of range (1..{dim})")



    @staticmethod
    def _replace_tokens(text: str, mapping: dict[str, str]) -> str:
        # longest-first to avoid overlaps
        for k in ("YYYY", "YY", "MMMM", "MMM", "MM", "M", "DD", "D"):
            text = text.replace(k, mapping[k])
        return text

    def _format_ad(self, d: _date, fmt: str, *, lang: Lang, ne_digits: bool) -> str:
        if lang == "ne":
            m_short = AD_MONTHS_NE[d.month - 1]
            m_full = m_short
        else:
            m_short = AD_MONTHS_EN[d.month - 1]
            m_full = m_short

        rep = {
            "YYYY": f"{d.year:04d}",
            "YY":   f"{d.year % 100:02d}",
            "MMMM": m_full,
            "MMM":  m_short,
            "MM":   f"{d.month:02d}",
            "M":    f"{d.month}",
            "DD":   f"{d.day:02d}",
            "D":    f"{d.day}",
        }
        out = self._replace_tokens(fmt, rep)
        return to_ne_digits(out) if (lang == "ne" and ne_digits) else out

    def _format_bs(self, b: BSDate, fmt: str, *, lang: Lang, ne_digits: bool) -> str:
        if not (1 <= b.month <= 12):
            raise ValidationError("BS month must be 1..12")
        if lang == "ne":
            m_short = BS_MONTHS_NE[b.month - 1]
            m_full = m_short
        else:
            m_short = BS_MONTHS_EN[b.month - 1]
            m_full = m_short

        rep = {
            "YYYY": f"{b.year:04d}",
            "YY":   f"{b.year % 100:02d}",
            "MMMM": m_full,
            "MMM":  m_short,
            "MM":   f"{b.month:02d}",
            "M":    f"{b.month}",
            "DD":   f"{b.day:02d}",
            "D":    f"{b.day}",
        }
        out = self._replace_tokens(fmt, rep)
        return to_ne_digits(out) if (lang == "ne" and ne_digits) else out



    def to_ad(
        self,
        bs,
        fmt: str | None = None,
        *,
        lang: Lang = "en",
        ne_digits: bool = False,
    ) -> _date | str:

        t = self._parse_bs(bs)
        self._validate_bs(t)

        cur = self._anchor_bs
        ad = self._anchor_ad
        step = 1 if (t.year, t.month, t.day) >= (cur.year, cur.month, cur.day) else -1

        while (cur.year, cur.month, cur.day) != (t.year, t.month, t.day):
            if step > 0:
                dim = self._years[str(cur.year)][cur.month - 1]
                if cur.day < dim:
                    cur = BSDate(cur.year, cur.month, cur.day + 1)
                else:
                    cur = BSDate(cur.year + 1, 1, 1) if cur.month == 12 else BSDate(cur.year, cur.month + 1, 1)
                ad += timedelta(days=1)
            else:
                if cur.day > 1:
                    cur = BSDate(cur.year, cur.month, cur.day - 1)
                else:
                    py = cur.year - 1 if cur.month == 1 else cur.year
                    pm = 12 if cur.month == 1 else cur.month - 1
                    dim = self._years[str(py)][pm - 1]
                    cur = BSDate(py, pm, dim)
                ad -= timedelta(days=1)

        if fmt:
            return self._format_ad(ad, fmt, lang=lang, ne_digits=ne_digits)
        return ad

    def to_bs(
        self,
        ad,
        fmt: str | None = None,
        *,
        lang: Lang = "en",
        ne_digits: bool = False,
    ) -> BSDate | str:

        delta = (self._parse_ad(ad) - self._anchor_ad).days
        cur = self._anchor_bs

        for _ in range(abs(delta)):
            if delta >= 0:
                dim_list = self._years.get(str(cur.year))
                if dim_list is None:
                    raise OutOfRangeError("AD outside BS coverage.")
                if cur.day < dim_list[cur.month - 1]:
                    cur = BSDate(cur.year, cur.month, cur.day + 1)
                else:
                    cur = BSDate(cur.year + 1, 1, 1) if cur.month == 12 else BSDate(cur.year, cur.month + 1, 1)
            else:
                if cur.day > 1:
                    cur = BSDate(cur.year, cur.month, cur.day - 1)
                else:
                    py = cur.year - 1 if cur.month == 1 else cur.year
                    pm = 12 if cur.month == 1 else cur.month - 1
                    dim = self._years[str(py)][pm - 1]
                    cur = BSDate(py, pm, dim)

        if fmt:
            return self._format_bs(cur, fmt, lang=lang, ne_digits=ne_digits)
        return cur




    def today_bs(
        self,
        fmt: str | None = None,
        *,
        lang: Lang = "en",
        ne_digits: bool = False,
    ) -> BSDate | str:
        
        today_ad = datetime.now(pytz.timezone(self.tz)).date()
        return self.to_bs(today_ad, fmt=fmt, lang=lang, ne_digits=ne_digits) if fmt else self.to_bs(today_ad)


    def now(
        self,
        fmt: str | None = None,
        *,
        lang: Lang = "en",
        ne_digits: bool = False,
    ) -> tuple[BSDate | str, datetime]:
        
        tz = pytz.timezone(self.tz)
        dt = datetime.now(tz)
        bs_part = self.to_bs(dt.date(), fmt=fmt, lang=lang, ne_digits=ne_digits) if fmt else self.to_bs(dt.date())
        return bs_part, dt
