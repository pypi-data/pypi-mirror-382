from __future__ import annotations
from typing import Dict, List

AREA_LARGE_FACTORS: Dict[str, float] = {
    "ropani": 508.72,
    "aana":   508.72 / 16.0,
    "paisa":  (508.72 / 16.0) / 4.0,
    "dam":    ((508.72 / 16.0) / 4.0) / 4.0,

    # Nepal (Terai system)
    "bigha":  6772.63,                       # 1 bigha = 6772.63 m²
    "kattha": 6772.63 / 20.0,                # 338.6315
    "dhur":   6772.63 / 400.0,    
    "hectare": 10_000.0,

    "m2": 1.0,
    "km2": 1000.0,
}

AREA_LARGE_ALIASES: Dict[str, List[str]] = {
    # Hill
    "ropani": ["ropani", "ropni", "रोपनी"],
    "aana":   ["aana", "anna", "ana", "आना", "आन्ना"],
    "paisa":  ["paisa", "paissa", "पैसा"],
    "dam":    ["dam", "daam", "डाम"],

    # Terai
    "bigha":  ["bigha", "biga", "बीघा", "बिघा"],
    "kattha": ["kattha", "katha", "कठ्ठा", "कत्ता"],
    "dhur":   ["dhur", "धुर"],

    # Metric big
    "hectare": ["hectare", "hectares", "ha", "हेक्टर"],
    "m2": ["meter", "meters", "metre", "metres", "मीटर"],
    "km2": ["kilometer", "kilometers", "kilometre", "kilometres", "किलोमिटर"],
}


AREA_SMALL_FACTORS: Dict[str, float] = {
    "m":    1.0,
    "cm":   0.01,
    "mm":   0.001,
    "km":   1000.0,
    "foot": 0.3048,
    "inch": 0.0254,
    "yard": 0.9144,
    
}

AREA_SMALL_ALIASES: Dict[str, List[str]] = {
    "m":  ["m", "meter", "meters", "metre", "metres", "मीटर"],
    "cm": ["cm", "centimeter", "centimeters", "centimetre", "centimetres"],
    "mm": ["mm", "millimeter", "millimeters", "millimetre", "millimetres"],
    "km": ["km", "kilometer", "kilometers", "kilometre", "kilometres", "किलोमिटर"],
    "foot": ["foot", "feet", "फुट"],
    "inch": ["inch", "इंच"],
    "yard": ["yard", "यार्ड"],
}

AREA_LARGE_BASE = "m2"

AREA_SMALL_BASE = "m"


VOLUME_FACTORS: Dict[str, float] = {
    "mana": 0.568261,
    "pathi": 0.568261 * 8.0,
    "muri": (0.568261 * 8.0) * 20.0,
    "liter": 1.0,
    "ml": 0.001,
}

VOLUME_ALIASES: Dict[str, List[str]] = {
    "mana":  ["mana", "माना", "मन"],
    "pathi": ["pathi", "pati", "पाथी", "पाती", "पाथि"],
    "muri":  ["muri", "मुरी"],
    "liter": ["liter", "litre", "liters", "litres", "l", "लीटर", " लीटर"],
    "ml":    ["ml", "milliliter", "millilitre", "milliliters", "millilitres", "mL"],
}

VOLUME_BASE = "L"


MASS_FACTORS: Dict[str, float] = {
    # Traditional (tola/masha/ratti expressed directly as kg)
    "tola":  11.6638038 / 1000.0,
    "masha": (11.6638038 / 12.0) / 1000.0,
    "ratti": ((11.6638038 / 12.0) / 8.0) / 1000.0,
    # Metric / Imperial
    "kg": 1.0,
    "g":  0.001,
    "lb": 0.45359237,
    "oz": 0.028349523125,
}

MASS_ALIASES: Dict[str, List[str]] = {
    "tola":  ["tola", "tolaa", "तोला", "तोलाे"],
    "masha": ["masha", "माशा"],
    "ratti": ["ratti", "rati", "रत्ती", "रत्‍ती", "रत्‍टी"],

    "kg": ["kg", "kilogram", "kilograms", "kilo", "किलो", "किलोग्राम", "किलो ग्राम"],
    "g":  ["g", "gram", "grams", "gm", "gms", "ग्राम"],
    "lb": ["lb", "lbs", "pound", "pounds", "पाउन्ड"],
    "oz": ["oz", "ounce", "ounces", "औन्स"],
}

MASS_BASE = "kg"

# =========================
# FINAL JSON-LIKE BUNDLE
# =========================
UNITS = {
    "large_area": {
        "base": AREA_LARGE_BASE,
        "factors": AREA_LARGE_FACTORS,
        "aliases": AREA_LARGE_ALIASES,
    },
    "small_area": {
        "base": AREA_SMALL_BASE,
        "factors": AREA_SMALL_FACTORS,
        "aliases": AREA_SMALL_ALIASES,
    },
    "volume": {
        "base": VOLUME_BASE,
        "factors": VOLUME_FACTORS,
        "aliases": VOLUME_ALIASES,
    },
    "mass": {
        "base": MASS_BASE,
        "factors": MASS_FACTORS,
        "aliases": MASS_ALIASES,
    },
}
