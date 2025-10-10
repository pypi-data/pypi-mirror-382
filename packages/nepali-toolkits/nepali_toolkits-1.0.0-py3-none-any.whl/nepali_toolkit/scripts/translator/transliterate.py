from __future__ import annotations

import json
from importlib.resources import files
from typing import Dict, List, Tuple


HALANT = "्"
MATRA_CHARS = set("ािीुूेैोौृ")
DEV_BLOCK_START, DEV_BLOCK_END = "\u0900", "\u097F"


class ScriptTransliterator:
    def __init__(self, load_exceptions: bool = True) -> None:
        path = files("nepali_toolkit.scripts.data") / "translit_data.json"
        self._data: Dict = json.loads(path.read_text(encoding="utf-8"))

        self.VOWELS: Dict[str, str] = dict(self._data["vowel_map"])
        self.MATRAS: Dict[str, str] = dict(self._data["matra_map"])
        self.CONSONANTS: Dict[str, str] = dict(self._data["consonant_map"])
        self.DIACRITICS: Dict[str, str] = dict(self._data["diacritic_map"])
        self.DEVANAGARI_DIGITS: str = self._data["dev_digits"]
        self.PRESERVE = set(self._data["preserve_chars"])

        self.DIGITS = {str(i): self.DEVANAGARI_DIGITS[i] for i in range(10)}

        self._exceptions: Dict[str, str] = {}
        if load_exceptions:
            try:
                pexc = files("nepali_toolkit.scripts.data") / "translit_exceptions.json"
                self._exceptions = json.loads(pexc.read_text(encoding="utf-8"))
            except FileNotFoundError:
                self._exceptions = {}

        self._ck = sorted(self.CONSONANTS.keys(), key=len, reverse=True)
        self._vk = sorted(self.VOWELS.keys(), key=len, reverse=True)
        self._mk = sorted(self.MATRAS.keys(), key=len, reverse=True)
        self._dk = sorted(self.DIACRITICS.keys(), key=len, reverse=True)


    def roman_to_dev(self, text: str) -> str:
        s = text.strip()
        if not s:
            return s
        low = s.lower()
        if low in self._exceptions:
            return self._exceptions[low]

        out: List[str] = []
        i = 0
        n = len(s)

  
        def previous_syllable_add_chandrabindu():
            if not out:
                return False
            out[-1] = out[-1] + "ँ"
            return True

        # For the "nt conjunct" request
        NT_CLUSTER_HEADS = ("t", "th")  # produce न् + (त/थ) for "...n[ t/th ]..."
        # If you want more conjunct triggers, extend this tuple.

        while i < n:
            ch = s[i:]
            c = s[i]

            # Digits
            if c.isdigit():
                out.append(self.DIGITS[c]); i += 1; continue

            # Spaces
            if c.isspace():
                out.append(c); i += 1; continue

            # Punctuation that we keep as-is
            if c in self.PRESERVE:
                out.append(c); i += 1; continue

            # Diacritics first (ṃ, ḥ, ~m → ं ः ँ)
            matched = False
            for d in self._dk:
                if ch.lower().startswith(d):
                    out.append(self.DIACRITICS[d]); i += len(d); matched = True; break
            if matched:
                continue

            # Special handling for 'n' (smart conjunct vs nasalize)
            if ch.lower().startswith("n"):
                # Lookahead for 't'/'th' (conjunct request: "santosh" → सन्तोष)
                nxt = None
                for cand in self._ck:  # check next consonant token
                    if s[i+1:].lower().startswith(cand):
                        nxt = cand
                        break

                if nxt in NT_CLUSTER_HEADS:
                    # Emit 'न्' + halant; do NOT consume the next consonant
                    out.append(self.CONSONANTS["n"] + HALANT)
                    i += 1
                    continue
                else:
                    # Else try nasalize previous syllable if it exists and we are before a consonant
                    if nxt is not None:
                        previous_syllable_add_chandrabindu()
                        i += 1  # consume 'n'
                        continue
                    # Otherwise, regular 'न'
                    out.append(self.CONSONANTS["n"])
                    i += 1
                    continue

            # Consonant?
            cons = None
            cons_key = None
            for ck in self._ck:
                if ch.lower().startswith(ck):
                    cons = self.CONSONANTS[ck]
                    cons_key = ck
                    i += len(ck)
                    break

            if cons is not None:
                # Try to attach a vowel matra right after the consonant
                vow = None
                rest = s[i:].lower()
                for v in self._mk:
                    if rest.startswith(v):
                        vow = v
                        break

                if vow:
                    # consonant + matra
                    out.append(cons + (self.MATRAS[vow] if vow else ""))
                    i += len(vow)
                    continue

                # No explicit vowel right after the consonant.
                # If the next token is another consonant, attach halant to conjunct.
                next_is_consonant = False
                for ck2 in self._ck:
                    if s[i:].lower().startswith(ck2):
                        next_is_consonant = True
                        break

                if next_is_consonant:
                    out.append(cons + HALANT)
                else:
                    # word-final or before space/punct → leave inherent 'a'
                    out.append(cons)
                continue

            # Pure vowel?
            vow = None
            for vk in self._vk:
                if ch.lower().startswith(vk):
                    out.append(self.VOWELS[vk])
                    i += len(vk)
                    vow = vk
                    break
            if vow:
                continue

            out.append(c)
            i += 1

        return "".join(out)


    def dev_to_roman(self, text: str) -> str:
        if not text:
            return text

        dev2rom = {v: k for k, v in self.CONSONANTS.items()}
        dev2rom.update({v: k for k, v in self.VOWELS.items()})
        dev2rom.update({v: k for k, v in self.DIACRITICS.items()})
        matra2rom = {v: k for k, v in self.MATRAS.items() if v}

        out: List[str] = []
        for ch in text:
            if ch == "ँ": out.append("~m"); continue
            if ch == "ं": out.append("ṃ");  continue
            if ch == "ः": out.append("ḥ");  continue
            if ch in self.DEVANAGARI_DIGITS:
                out.append(str(self.DEVANAGARI_DIGITS.index(ch))); continue
            if ch in matra2rom:
                out.append(matra2rom[ch]); continue
            if ch == "्":  # halant: generally suppress inherent 'a'
                out.append("")            # handled by next consonant in consumers
                continue
            out.append(dev2rom.get(ch, ch))

        return "".join(out)
