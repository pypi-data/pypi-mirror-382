# src/nepali_toolkit/gazetteer/__init__.py
from __future__ import annotations

from typing import Iterable, Optional, Dict, List

from .gazetteer import GazetteerService  # the class you pasted

__all__ = [
    # admin lookups
    "list_provinces", "get_province",
    "list_zones", "get_zone",
    "list_districts", "get_district",
    # places
    "get_place",
    "list_places", "nearby_places", "list_famous_places",
]

# ---------- singleton backing ----------
_srv: Optional[GazetteerService] = None

def configure() -> None:
    """
    Initialize (or reinitialize) the shared GazetteerService instance.
    Call once at app startup if you want to reload JSONs.
    """
    global _srv
    _srv = GazetteerService()

def _svc() -> GazetteerService:
    global _srv
    if _srv is None:
        _srv = GazetteerService()
    return _srv

# ---------- admin: provinces / zones / districts ----------

def list_provinces() -> List[Dict]:
    return _svc().list_provinces()

def get_province(code_or_name: str) -> Optional[Dict]:
    return _svc().get_province(code_or_name)

def list_zones() -> List[Dict]:
    return _svc().list_zones()

def get_zone(code_or_name: str) -> Optional[Dict]:
    return _svc().get_zone(code_or_name)

def list_districts(
    *,
    zone: Optional[str] = None,
    province: Optional[str] = None,
    name_contains: Optional[str] = None,
) -> List[Dict]:
    return _svc().list_districts(zone=zone, province=province, name_contains=name_contains)

def get_district(code_or_name: str) -> Optional[Dict]:
    return _svc().get_district(code_or_name)

# ---------- places ----------

def get_place(slug_or_name: str) -> Optional[Dict]:
    return _svc().get_place(slug_or_name)

def query_places(
    *,
    province: Optional[str] = None,
    zone: Optional[str] = None,
    district: Optional[str] = None,
    tags_any: Optional[Iterable[str]] = None,
    tags_all: Optional[Iterable[str]] = None,
    famous_only: bool = False,
    query: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: Optional[float] = None,
    include_distance: bool = True,
    sort_by: str = "name",   # "distance" | "score" | "name"
    limit: Optional[int] = None,
) -> List[Dict]:
    return _svc().query_places(
        province=province, zone=zone, district=district,
        tags_any=tags_any, tags_all=tags_all, famous_only=famous_only,
        query=query, lat=lat, lng=lng, radius_km=radius_km,
        include_distance=include_distance, sort_by=sort_by, limit=limit,
    )

def list_places(**kwargs) -> List[Dict]:
    return _svc().list_places(**kwargs)

def nearby_places(lat: float, lng: float, **kwargs) -> List[Dict]:
    return _svc().nearby_places(lat, lng, **kwargs)

def list_famous_places(**kwargs) -> List[Dict]:
    return _svc().list_famous_places(**kwargs)
