from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Iterable, Union, Literal, Sequence
import json
from importlib.resources import files



@dataclass(frozen=True)
class AlphabetItem:
    roman: str
    dev: str
    example_ne: Optional[str] = None
    example_en: Optional[str] = None


_DATA_CACHE: Optional[dict] = None

def _load_data_cached() -> dict:
    global _DATA_CACHE
    if _DATA_CACHE is None:
        p = files("nepali_toolkit.scripts.data") / "translit_data.json"
        _DATA_CACHE = json.loads(p.read_text(encoding="utf-8"))
    return _DATA_CACHE

def _build_items_from_explicit(block: list) -> List[AlphabetItem]:
    return [
        AlphabetItem(
            roman=entry["roman"],
            dev=entry["dev"],
            example_ne=entry.get("example_ne"),
            example_en=entry.get("example_en"),
        )
        for entry in block
    ]

def _build_items_from_map(map_block: dict) -> List[AlphabetItem]:
    return [AlphabetItem(roman=r, dev=d) for r, d in map_block.items()]




class AlphabetCatalog:

    def __init__(self) -> None:
        data = _load_data_cached()

        if isinstance(data.get("vowels"), list):
            vowels = _build_items_from_explicit(data["vowels"])
        else:
            vowels = _build_items_from_map(data.get("vowel_map", {}))

        order_keys: Sequence[str] = data.get("barakhari_vowel_order") or [v.roman for v in vowels]
        order_index = {k: i for i, k in enumerate(order_keys)}
        vowels.sort(key=lambda it: order_index.get(it.roman, 10_000))

        if isinstance(data.get("consonants"), list):
            consonants = _build_items_from_explicit(data["consonants"])
        else:
            consonants = _build_items_from_map(data.get("consonant_map", {}))

        self._vowels: List[AlphabetItem] = vowels
        self._consonants: List[AlphabetItem] = consonants

        self._vowels_by_roman: Dict[str, AlphabetItem] = {v.roman: v for v in vowels}
        self._vowels_by_dev:   Dict[str, AlphabetItem] = {v.dev: v for v in vowels}
        self._cons_by_roman:   Dict[str, AlphabetItem] = {c.roman: c for c in consonants}
        self._cons_by_dev:     Dict[str, AlphabetItem] = {c.dev: c for c in consonants}


    @property
    def vowels(self) -> List[AlphabetItem]:
        return list(self._vowels)

    @property
    def consonants(self) -> List[AlphabetItem]:
        return list(self._consonants)

    @property
    def vowels_by_roman(self) -> Dict[str, AlphabetItem]:
        return dict(self._vowels_by_roman)

    @property
    def vowels_by_dev(self) -> Dict[str, AlphabetItem]:
        return dict(self._vowels_by_dev)

    @property
    def consonants_by_roman(self) -> Dict[str, AlphabetItem]:
        return dict(self._cons_by_roman)

    @property
    def consonants_by_dev(self) -> Dict[str, AlphabetItem]:
        return dict(self._cons_by_dev)


    @staticmethod
    def _normalize_select(select: Optional[Union[str, Iterable[str]]]) -> Optional[List[str]]:

        if select is None:
            return None
        if isinstance(select, (str, bytes)):
            s = select.strip()
            return [s] if s else None

        cleaned = [s.strip() for s in select if isinstance(s, str) and s.strip()]
        return cleaned or None

    @staticmethod
    def _filter_examples(items: List[AlphabetItem], example_only: bool) -> List[AlphabetItem]:
        if not example_only:
            return items
        return [it for it in items if (it.example_ne or it.example_en)]

    def _pick_by_keys(
        self,
        items: List[AlphabetItem],
        by_roman: Dict[str, AlphabetItem],
        by_dev: Dict[str, AlphabetItem],
        select: Optional[Union[str, Iterable[str]]],
        example_only: bool,
    ) -> List[AlphabetItem]:

        keys = self._normalize_select(select)
        if keys is None:
            return self._filter_examples(list(items), example_only)

        picked: List[AlphabetItem] = []
        seen: set[str] = set()
        for k in keys:
            it = by_roman.get(k) or by_dev.get(k)
            if it and (it.roman not in seen):
                seen.add(it.roman)
                picked.append(it)
        return self._filter_examples(picked, example_only)



    def consonant_alphabet(
        self,
        select: Optional[Union[str, Iterable[str]]] = None,
        *,
        out: Literal["dev", "roman", "pair"] = "pair",
        example: bool = False,
    ):
        items = self._pick_by_keys(
            self._vowels, self._vowels_by_roman, self._vowels_by_dev, select, example_only=False
        )

        if out == "dev":
            base_rows = [{"dev": it.dev} for it in items]
        elif out == "roman":
            base_rows = [{"roman": it.roman} for it in items]
        else:
            base_rows = [{"roman": it.roman, "dev": it.dev} for it in items]

        if not example:
            return base_rows

        formatted = []
        for row, it in zip(base_rows, items):
            
            row_with_examples = dict(row)
            row_with_examples["example_ne"] = it.example_ne
            row_with_examples["example_en"] = it.example_en
            formatted.append(row_with_examples)
        return formatted


    def vowel_alphabet(
        self,
        select: Optional[Union[str, Iterable[str]]] = None,
        *,
        out: Literal["dev", "roman", "pair"] = "pair",
        example: bool = False,
    ):
        items = self._pick_by_keys(
            self._vowels, self._vowels_by_roman, self._vowels_by_dev, select, example_only=False
        )

        if out == "dev":
            base_rows = [{"dev": it.dev} for it in items]
        elif out == "roman":
            base_rows = [{"roman": it.roman} for it in items]
        else:
            base_rows = [{"roman": it.roman, "dev": it.dev} for it in items]

        if not example:
            return base_rows

        formatted = []
        for row, it in zip(base_rows, items):
            
            row_with_examples = dict(row)
            row_with_examples["example_ne"] = it.example_ne
            row_with_examples["example_en"] = it.example_en
            formatted.append(row_with_examples)
        return formatted


_catalog = AlphabetCatalog()

VOWELS = _catalog.vowels
CONSONANTS = _catalog.consonants
VOWELS_BY_ROMAN = _catalog.vowels_by_roman
VOWELS_BY_DEV   = _catalog.vowels_by_dev
CONSONANTS_BY_ROMAN = _catalog.consonants_by_roman
CONSONANTS_BY_DEV   = _catalog.consonants_by_dev
