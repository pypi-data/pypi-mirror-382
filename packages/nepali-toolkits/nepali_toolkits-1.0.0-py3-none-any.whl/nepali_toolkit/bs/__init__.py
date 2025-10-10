# nepali_toolkit/bs/__init__.py
from __future__ import annotations

from typing import Optional, Tuple
from datetime import date as _date, datetime

from .calendar import BSCalendar
from .types import BSDate

__all__ = [
    "to_bs",
    "to_ad",
    "today_bs",
    "now",
]

# ---- shared calendar (lazy) ------------------------------------------------

_default_tz = "Asia/Kathmandu"
_cal: Optional[BSCalendar] = None

def get_calendar() -> BSCalendar:
    """Return the shared BSCalendar instance used by the function-style API."""
    global _cal
    if _cal is None:
        _cal = BSCalendar(_default_tz)
    return _cal

def configure(*, tz: str = "Asia/Kathmandu") -> None:
    """
    Configure the default timezone for the function-style API.
    Example:
        from nepali_toolkit.bs import configure
        configure(tz="Asia/Kathmandu")
    """
    global _cal, _default_tz
    _default_tz = tz
    _cal = BSCalendar(tz)

# ---- function-style helpers ------------------------------------------------

def to_bs(ad, fmt: Optional[str] = None, *, lang: str = "en", ne_digits: bool = False):
    """
    Gregorian (AD) -> Bikram Sambat (BS)
    - ad: datetime.date or ISO 'YYYY-MM-DD'
    - fmt: if provided, returns str; else returns BSDate
    - lang: 'en' or 'ne'
    - ne_digits: Nepali digits when lang='ne'
    """
    cal = get_calendar()
    return cal.to_bs(ad, fmt=fmt, lang=lang, ne_digits=ne_digits)

def to_ad(bs, fmt: Optional[str] = None, *, lang: str = "en", ne_digits: bool = False) -> _date | str:
    """
    Bikram Sambat (BS) -> Gregorian (AD)
    - bs: BSDate or BS ISO 'YYYY-MM-DD'
    - fmt/lang/ne_digits same as to_bs
    """
    cal = get_calendar()
    return cal.to_ad(bs, fmt=fmt, lang=lang, ne_digits=ne_digits)

def today_bs(fmt: Optional[str] = None, *, lang: str = "en", ne_digits: bool = False) -> BSDate | str:
    """Today’s BS date in the configured timezone."""
    cal = get_calendar()
    return cal.today_bs(fmt=fmt, lang=lang, ne_digits=ne_digits)

def now(fmt: Optional[str] = None, *, lang: str = "en", ne_digits: bool = False) -> Tuple[BSDate | str, datetime]:
    """
    Current moment: (BS part, aware AD datetime).
    If fmt is provided, BS part is a formatted string; otherwise a BSDate.
    """
    cal = get_calendar()
    return cal.now(fmt=fmt, lang=lang, ne_digits=ne_digits)
