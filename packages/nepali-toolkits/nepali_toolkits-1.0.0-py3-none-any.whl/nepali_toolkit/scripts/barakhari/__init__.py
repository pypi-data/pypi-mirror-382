from .barakhari import Barakhari


# Shared instance
__b = Barakhari()

def table(bases=None, *, out: str = "dev"):
    """Barakhari table for bases (or all by default)."""
    return __b.table(bases, out=out)


__all__ = [
    "table",
]
