# src/nepali_toolkit/trek/__init__.py
from __future__ import annotations

from typing import Iterable, Optional, Dict, List

from .catalog import TrekCatalog

__all__ = [
    "list_treks",
    "get_trek",
    "search_treks",
    "nearby_treks",
    "suggest",
]

# ---- internal lazy singleton ----
_svc: Optional[TrekCatalog] = None

def configure() -> None:
    """
    (Optional) Manually reinitialize the shared TrekCatalog.
    Useful if you change data files at runtime (mostly for tests).
    """
    global _svc
    _svc = TrekCatalog()

def _service() -> TrekCatalog:
    global _svc
    if _svc is None:
        _svc = TrekCatalog()
    return _svc

# ---- public function API ----

def list_treks() -> List[Dict]:
    """Return all treks as a list of dicts."""
    return _service().list_treks()

def get_trek(slug_or_name: str) -> Optional[Dict]:
    """Lookup a trek by slug or name (English/Nepali)."""
    return _service().get_trek(slug_or_name)

def query_treks(
    *,
    provinces: Optional[Iterable[str]] = None,
    districts: Optional[Iterable[str]] = None,
    region_contains: Optional[str] = None,
    difficulty: Optional[Iterable[str]] = None,
    permit_any: Optional[Iterable[str]] = None,
    permit_all: Optional[Iterable[str]] = None,
    tags_any: Optional[Iterable[str]] = None,
    tags_all: Optional[Iterable[str]] = None,
    seasons_any: Optional[Iterable[str]] = None,
    days_min: Optional[int] = None,
    days_max: Optional[int] = None,
    alt_min: Optional[int] = None,
    alt_max: Optional[int] = None,
    query: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: Optional[float] = None,
    include_distance: bool = True,
    sort_by: str = "name",  # "distance" | "score" | "name" | "days" | "alt"
    limit: Optional[int] = None,
) -> List[Dict]:
    """
    Unified trek search/filter. See TrekCatalog.query_treks docstring for details.
    """
    return _service().query_treks(
        provinces=provinces,
        districts=districts,
        region_contains=region_contains,
        difficulty=difficulty,
        permit_any=permit_any,
        permit_all=permit_all,
        tags_any=tags_any,
        tags_all=tags_all,
        seasons_any=seasons_any,
        days_min=days_min,
        days_max=days_max,
        alt_min=alt_min,
        alt_max=alt_max,
        query=query,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        include_distance=include_distance,
        sort_by=sort_by,
        limit=limit,
    )

def search_treks(query: str, **kwargs) -> List[Dict]:
    """Ranked text search; convenience wrapper around query_treks(query=...)."""
    return _service().search_treks(query, **kwargs)

def nearby_treks(lat: float, lng: float, **kwargs) -> List[Dict]:
    """
    Treks whose start point is within a radius (km) of (lat,lng).
    Default radius_km=50 and sort_by='distance' (can be overridden in kwargs).
    """
    return _service().nearby_treks(lat, lng, **kwargs)

def suggest(prefix: str, *, limit: int = 8) -> List[Dict]:
    """Simple autocomplete by slug/name/region/tags/highlights."""
    return _service().suggest(prefix, limit=limit)
