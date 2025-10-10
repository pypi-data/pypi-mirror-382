from __future__ import annotations

__all__ = [
    "NE_DIGITS",
    "to_ne_digits",
    "to_ascii_digits",
    "plural_ne",
    "BS_MONTHS_EN",
    "BS_MONTHS_NE",
    "AD_MONTHS_EN",
    "AD_MONTHS_NE",
    "WEEKDAYS_EN",
    "WEEKDAYS_NE",
    "ne_digits_if",
    "ordinal_en",
    "format_number",
    "join_with",
]

NE_DIGITS = "०१२३४५६७८९"
_ASCII_TO_NE = {str(i): NE_DIGITS[i] for i in range(10)}
_NE_TO_ASCII = {NE_DIGITS[i]: str(i) for i in range(10)}

def to_ne_digits(s: str) -> str:
    """Convert ASCII digits 0–9 in s to Nepali digits."""
    out: list[str] = []
    for ch in str(s):
        out.append(_ASCII_TO_NE.get(ch, ch))
    return "".join(out)

def to_ascii_digits(s: str) -> str:
    """Convert Nepali digits in s to ASCII digits 0–9."""
    return "".join(_NE_TO_ASCII.get(ch, ch) for ch in str(s))

def ne_digits_if(s: str, use_ne: bool) -> str:
    """Return s with Nepali digits if use_ne=True; otherwise return s unchanged."""
    return to_ne_digits(s) if use_ne else s

def format_number(n, *, nepali: bool = False) -> str:
    """
    Format a number as string; if nepali=True, render digits in Nepali.
    (No locale/grouping to keep it deterministic for devs.)
    """
    s = str(n)
    return to_ne_digits(s) if nepali else s

BS_MONTHS_EN = [
    "Baisakh","Jestha","Ashadh","Shrawan","Bhadra","Ashoj",
    "Kartik","Mangsir","Poush","Magh","Falgun","Chaitra",
]

BS_MONTHS_NE = [
    "बैशाख","जेठ","आषाढ","श्रावण","भदौ","आश्विन",
    "कार्तिक","मंसिर","पौष","माघ","फाल्गुण","चैत",
]

AD_MONTHS_EN = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
AD_MONTHS_NE = ["जनवरी","फेब्रुअरी","मार्च","अप्रिल","मे","जुन","जुलाई","अगस्ट","सेप्टेम्बर","अक्टोबर","नोभेम्बर","डिसेम्बर"]


WEEKDAYS_EN = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
WEEKDAYS_NE = ["सोम","मङ्गल","बुध","बिही","शुक्र","शनि","आइत"]


def plural_ne(n: int, singular: str, plural: str) -> str:
    return singular if n == 1 else plural

def ordinal_en(n: int, *, nepali_digits: bool = False) -> str:
    sfx = "th"
    if not 11 <= (n % 100) <= 13:
        last = n % 10
        if last == 1: sfx = "st"
        elif last == 2: sfx = "nd"
        elif last == 3: sfx = "rd"
    num = to_ne_digits(n) if nepali_digits else str(n)
    return f"{num}{sfx}"


def join_with(items, sep: str = " ", *, nepali_digits: bool = False) -> str:
    s = sep.join(map(str, items))
    return to_ne_digits(s) if nepali_digits else s
