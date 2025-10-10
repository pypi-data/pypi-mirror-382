from __future__ import annotations

from typing import List, Tuple, Literal, Iterable, Dict, Optional, Union
import json
from importlib.resources import files

from ..alphabet.alphabets import CONSONANTS, CONSONANTS_BY_DEV, CONSONANTS_BY_ROMAN
from ..translator.transliterate import ScriptTransliterator

HALANT = "्"
MATRA_CHARS = set("ािीुूेैोौृ")

def _load_core_order() -> List[str]:
    p = files("nepali_toolkit.scripts.data") / "translit_data.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    return list(data["barakhari_vowel_order"])

def _roman_syllable(base: str, vkey: str) -> str:
    suffix = {
        "a": "", "aa": "aa",
        "i": "i", "ii": "ii",
        "u": "u", "uu": "uu",
        "e": "e", "ai": "ai",
        "o": "o", "au": "au",
        "ri": "ri",
    }[vkey]
    return base if vkey == "a" else base + suffix

def _strip_trailing_matra(dev: str) -> str:
    """Remove a single trailing matra/halant to get the base consonant cluster."""
    if not dev:
        return dev
    if dev[-1] in MATRA_CHARS or dev[-1] == HALANT:
        return dev[:-1]
    return dev

class Barakhari:

    def __init__(self, translit: ScriptTransliterator | None = None):
        self.t = translit or ScriptTransliterator()
        self._order: List[str] = _load_core_order()
        # Default “show all” = every consonant (dev form)
        self._default_bases_dev: List[str] = [c.dev for c in CONSONANTS]

    def _resolve_base(self, base: str) -> Tuple[str, str]:

        b = (base or "").strip()
        if not b:
            return "", ""

        # If Devanagari input, strip trailing matra/halant to get the base
        if "\u0900" <= b[0] <= "\u097F":
            dev_base = _strip_trailing_matra(b)
            # Exact known consonant?
            if dev_base in CONSONANTS_BY_DEV:
                return CONSONANTS_BY_DEV[dev_base].roman, dev_base
            # Best effort: transliterate to roman and try again
            roman_guess = self.t.dev_to_roman(dev_base)
            # If roman_guess is a known consonant, use that
            if roman_guess in CONSONANTS_BY_ROMAN:
                return roman_guess, CONSONANTS_BY_ROMAN[roman_guess].dev
            return roman_guess, dev_base  # fallback (still consonant-ish)

        # Roman input
        low = b.lower()

        # Exact consonant key?
        if low in CONSONANTS_BY_ROMAN:
            return low, CONSONANTS_BY_ROMAN[low].dev

        # If endswith 'a', try removing the inherent 'a' (e.g., 'ka' → 'k')
        if low.endswith("a") and low[:-1] in CONSONANTS_BY_ROMAN:
            r = low[:-1]
            return r, CONSONANTS_BY_ROMAN[r].dev

        # Fallback: roman→dev, then strip matra to get base
        dev_guess = self.t.roman_to_dev(low)           # e.g. 'ka' → 'का'
        dev_base  = _strip_trailing_matra(dev_guess)   # 'का'  → 'क'
        if dev_base in CONSONANTS_BY_DEV:
            return CONSONANTS_BY_DEV[dev_base].roman, dev_base

        # Last resort: treat as-is (may not be a pure consonant)
        roman_guess = self.t.dev_to_roman(dev_base)
        return roman_guess, dev_base

    def row(
        self,
        base: str,
        *,
        out: Literal["dev", "roman", "pair"] = "dev"
    ) -> List[str] | List[Tuple[str, str]]:
        r_base, dev_base = self._resolve_base(base)
        if not r_base or not dev_base:
            return []

        romans: List[str] = []
        devs: List[str] = []
        for key in self._order:
            if key == "a":
                romans.append(r_base)
                devs.append(dev_base)
            else:
                romans.append(_roman_syllable(r_base, key))
                devs.append(dev_base + self.t.MATRAS[key])

        if out == "dev":
            return devs
        if out == "roman":
            return romans
        return list(zip(romans, devs))

    def table(
        self,
        bases: Optional[Union[str, Iterable[str]]] = None,
        *,
        out: Literal["dev", "roman", "pair"] = "dev"
    ) -> List[List[str]] | List[List[Tuple[str, str]]]:
        
        if bases is None:
            bases_list = self._default_bases_dev
        elif isinstance(bases, str):
            bases_list = [bases]  # ← key fix: single base
        else:
            bases_list = list(bases) or self._default_bases_dev

        return [self.row(b, out=out) for b in bases_list]