from __future__ import annotations
from typing import Dict, Optional, Tuple
from .profiles import UNITS

def _norm(s: str) -> str:
    """Normalize whitespace + case + common superscripts for alias matching."""
    return " ".join(
        (s or "")
        .strip()
        .casefold()
        .replace("²", "2")
        .replace("³", "3")
        .split()
    )

def _build_alias_maps() -> Dict[str, Dict[str, str]]:
    """
    For each category, build: alias (normalized) -> canonical unit key.
    """
    out: Dict[str, Dict[str, str]] = {}
    for cat, spec in UNITS.items():
        amap: Dict[str, str] = {}
        for canon, arr in spec.get("aliases", {}).items():
            amap[_norm(canon)] = canon
            for a in arr:
                amap[_norm(a)] = canon
        out[cat] = amap
    return out

_ALIAS = _build_alias_maps()

def _resolve(unit: str) -> Optional[Tuple[str, str]]:
    """
    Resolve any unit alias to (category, canonical_unit).
    Returns None if unknown.
    """
    key = _norm(unit)
    for cat, amap in _ALIAS.items():
        if key in amap:
            return cat, amap[key]
    return None

class UnitConverter:
    """
    Single API:
        convert(value: float, from_unit: str, to_unit: str) -> float

    - Data-driven: relies on UNITS in profiles.py
    - Enforces same-category conversion (area/volume/mass)
    - Converts value -> base -> target, using factors to the category base.
    """

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        src = _resolve(from_unit)
        dst = _resolve(to_unit)

        if src is None:
            raise ValueError(f"Unknown unit: {from_unit!r}")
        if dst is None:
            raise ValueError(f"Unknown unit: {to_unit!r}")

        src_cat, src_canon = src
        dst_cat, dst_canon = dst
        if src_cat != dst_cat:
            raise ValueError(f"Category mismatch: '{from_unit}' is {src_cat}, but '{to_unit}' is {dst_cat}")

        spec = UNITS[src_cat]
        base = spec["base"]                      # e.g., "m2", "L", "kg"
        factors: Dict[str, float] = spec["factors"]

        # Ensure the base exists (usually does; safety fallback)
        if base not in factors:
            factors = {**factors, base: 1.0}

        if src_canon not in factors:
            raise ValueError(f"Missing factor for source unit '{src_canon}' in category '{src_cat}'")
        if dst_canon not in factors:
            raise ValueError(f"Missing factor for target unit '{dst_canon}' in category '{dst_cat}'")

        # Convert to base, then to destination
        in_base = value * factors[src_canon]
        out_val = in_base / factors[dst_canon]
        return out_val