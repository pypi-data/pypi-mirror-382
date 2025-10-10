from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Province:
    code: str
    name_en: str
    name_ne: Optional[str] = None
    capital_en: Optional[str] = None
    capital_ne: Optional[str] = None

    def model_dump(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name_en": self.name_en,
            "name_ne": self.name_ne,
            "capital_en": self.capital_en,
            "capital_ne": self.capital_ne,
        }


@dataclass
class Zone:
    code: str
    name_en: str
    name_ne: Optional[str] = None
    # legacy zones typically don't have province linkage in old datasets,
    # but include it if your JSON provides it
    province_code: Optional[str] = None

    def model_dump(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name_en": self.name_en,
            "name_ne": self.name_ne,
            "province_code": self.province_code,
        }


@dataclass
class District:
    code: str
    name_en: str
    name_ne: Optional[str] = None
    zone_code: Optional[str] = None
    province_code: Optional[str] = None
    hq_en: Optional[str] = None
    hq_ne: Optional[str] = None

    def model_dump(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name_en": self.name_en,
            "name_ne": self.name_ne,
            "zone_code": self.zone_code,
            "province_code": self.province_code,
            "hq_en": self.hq_en,
            "hq_ne": self.hq_ne,
        }


@dataclass
class PlaceItem:
    # identity
    slug: str
    name_en: str
    # labels
    name_ne: Optional[str] = None
    alt_names: List[str] = field(default_factory=list)
    # classification / filters
    kind: Optional[str] = None            # e.g., "place", "palace", "temple", "museum", "peak"...
    tags: List[str] = field(default_factory=list)
    famous: bool = False
    # admin linkage
    province_code: Optional[str] = None
    zone_code: Optional[str] = None
    district_code: Optional[str] = None
    # geo
    lat: Optional[float] = None
    lng: Optional[float] = None
    elev_m: Optional[int] = None
    # misc metadata
    description: Optional[str] = None
    wiki: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None

    def model_dump(self) -> Dict[str, Any]:
        return {
            "slug": self.slug,
            "name_en": self.name_en,
            "name_ne": self.name_ne,
            "alt_names": list(self.alt_names or []),
            "kind": self.kind,
            "tags": list(self.tags or []),
            "famous": bool(self.famous),
            "province_code": self.province_code,
            "zone_code": self.zone_code,
            "district_code": self.district_code,
            "lat": self.lat,
            "lng": self.lng,
            "elev_m": self.elev_m,
            "description": self.description,
            "wiki": self.wiki,
            "website": self.website,
            "phone": self.phone,
        }
