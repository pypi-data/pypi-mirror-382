# src/nepali_toolkit/unit/__init__.py
from __future__ import annotations

from typing import Union

from .converter import UnitConverter

__all__ = [
    "convert"
]

# Single shared instance for convenience
_converter = UnitConverter()

def convert(value: Union[int, float], from_unit: str, to_unit: str) -> float:
    return _converter.convert(float(value), from_unit, to_unit)
