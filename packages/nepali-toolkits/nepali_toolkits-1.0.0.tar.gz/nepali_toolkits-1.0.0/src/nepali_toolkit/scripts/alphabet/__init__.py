from __future__ import annotations

from typing import Iterable, Optional, Union, Literal, List, Dict

from .alphabets import AlphabetCatalog

__all__ = [
    "vowel_alphabet",
    "consonant_alphabet",
    "vowels_",
    "consonants_",
]

_catalog = AlphabetCatalog()

def vowel_alphabet(
    select: Optional[Union[str, Iterable[str]]] = None,
    *,
    out: Literal["dev", "roman", "pair"] = "pair",
    example: bool = False,
) -> List[Dict]:
    """
    Convenience wrapper around AlphabetCatalog.vowel_alphabet()

    Examples:
        vowel_alphabet(out="dev")
        vowel_alphabet(out="roman", example=True)
        vowel_alphabet(select=["a", "aa"], out="pair")
        vowel_alphabet(select="अ", out="pair", example=True)
    """
    return _catalog.vowel_alphabet(select, out=out, example=example)

def consonant_alphabet(
    select: Optional[Union[str, Iterable[str]]] = None,
    *,
    out: Literal["dev", "roman", "pair"] = "pair",
    example: bool = False,
) -> List[Dict]:
    """
    Convenience wrapper around AlphabetCatalog.consonant_alphabet()

    Examples:
        consonant_alphabet(out="dev")
        consonant_alphabet(select=["ka","kha","ga"], out="pair", example=True)
        consonant_alphabet(select="क", out="roman")
    """
    return _catalog.consonant_alphabet(select, out=out, example=example)

vowels_ = _catalog.vowels
consonants_ = _catalog.consonants
