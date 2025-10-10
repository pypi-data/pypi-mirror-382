from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class TrekStage:
    day: int
    title: str
    desc: Optional[str] = None
    frm: Optional[str] = None     # "from" is reserved keyword in Python
    to: Optional[str] = None
    alt_m: Optional[int] = None
    distance_km: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

@dataclass
class TrekRoute:
    slug: str
    name_en: str
    name_ne: Optional[str] = None

    region: Optional[str] = None          # e.g. "Everest/Solukhumbu", "Annapurna/Kaski"
    provinces: List[str] = field(default_factory=list)   # e.g. ["P1","P4"]
    districts: List[str] = field(default_factory=list)   # e.g. ["SOL","KAS"]

    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None

    min_alt_m: Optional[int] = None
    max_alt_m: Optional[int] = None
    days: Optional[int] = None
    distance_km: Optional[float] = None

    difficulty: Optional[str] = None      # "easy" | "moderate" | "challenging" | "strenuous"
    permits: List[str] = field(default_factory=list)     # e.g. ["TIMS","ACAP","MCAP","RAP"]
    seasons: List[str] = field(default_factory=list)     # e.g. ["spring","autumn"]

    tags: List[str] = field(default_factory=list)        # free-form tags
    highlights: List[str] = field(default_factory=list)
    overview: Optional[str] = None

    stages: List[TrekStage] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TrekRoute":
        stages = [TrekStage(**s) for s in d.get("stages", [])]
        return cls(
            slug=d["slug"],
            name_en=d["name_en"],
            name_ne=d.get("name_ne"),
            region=d.get("region"),
            provinces=list(d.get("provinces", [])),
            districts=list(d.get("districts", [])),
            start_lat=d.get("start_lat"),
            start_lng=d.get("start_lng"),
            end_lat=d.get("end_lat"),
            end_lng=d.get("end_lng"),
            min_alt_m=d.get("min_alt_m"),
            max_alt_m=d.get("max_alt_m"),
            days=d.get("days"),
            distance_km=d.get("distance_km"),
            difficulty=d.get("difficulty"),
            permits=list(d.get("permits", [])),
            seasons=list(d.get("seasons", [])),
            tags=list(d.get("tags", [])),
            highlights=list(d.get("highlights", [])),
            overview=d.get("overview"),
            stages=stages,
        )

    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        d["stages"] = [s.__dict__.copy() for s in self.stages]
        return d
