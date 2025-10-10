from .transliterate import ScriptTransliterator

# Singleton for convenience
__t = ScriptTransliterator()

def roman_to_dev(text: str) -> str:
    """Romanized Nepali → Devanagari."""
    return __t.roman_to_dev(text)

def dev_to_roman(text: str) -> str:
    """Devanagari → Romanized Nepali."""
    return __t.dev_to_roman(text)

__all__ = [
    "roman_to_dev",
    "dev_to_roman",
]
