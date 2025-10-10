from __future__ import annotations

from typing import List, Dict, Optional, Iterable, Tuple
import math

from nepali_toolkit.common.util import read_json_resource
from .models import Province, Zone, District, PlaceItem


# --------------------- helpers ---------------------

def _norm(s: str) -> str:
    return (s or "").casefold().strip()

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two (lat,lng) in kilometers."""
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))


# ===================== CATALOG =====================

class GazetteerService:
    def __init__(self):
        # Provinces (required)
        self._provinces: List[Province] = [
            Province(**p)
            for p in read_json_resource("nepali_toolkit.gazetteer.data", "provinces.json")
        ]

        try:
            _zones_raw = read_json_resource("nepali_toolkit.gazetteer.data", "zones.json")
        except Exception:
            _zones_raw = []
        try:
            _districts_raw = read_json_resource("nepali_toolkit.gazetteer.data", "districts.json")
        except Exception:
            _districts_raw = []

        self._zones: List[Zone] = [Zone(**z) for z in _zones_raw]
        self._districts: List[District] = [District(**d) for d in _districts_raw]

        # Single unified places file
        self._places: List[PlaceItem] = [
            PlaceItem(**p)
            for p in read_json_resource("nepali_toolkit.gazetteer.data", "places.json")
        ]

        # Index maps
        self._p_by_code: Dict[str, Province] = {p.code: p for p in self._provinces}
        self._z_by_code: Dict[str, Zone] = {z.code: z for z in self._zones}
        self._d_by_code: Dict[str, District] = {d.code: d for d in self._districts}
        self._places_by_slug: Dict[str, PlaceItem] = {
            _norm(pl.slug): pl for pl in self._places if getattr(pl, "slug", None)
        }

    # ------------------ minimal lookups ------------------

    def list_provinces(self) -> List[Dict]:
        return [p.__dict__ for p in self._provinces]

    def get_province(self, code_or_name: str) -> Optional[Dict]:
        k = _norm(code_or_name)
        for p in self._provinces:
            if _norm(p.code) == k or _norm(p.name_en) == k or _norm(p.name_ne) == k:
                return p.__dict__
        return None

    def list_zones(self) -> List[Dict]:
        return [z.__dict__ for z in self._zones]

    def get_zone(self, code_or_name: str) -> Optional[Dict]:
        k = _norm(code_or_name)
        for z in self._zones:
            if _norm(z.code) == k or _norm(z.name_en) == k or _norm(z.name_ne) == k:
                return z.__dict__
        return None

    def list_districts(
        self,
        *,
        zone: Optional[str] = None,
        province: Optional[str] = None,
        name_contains: Optional[str] = None,
    ) -> List[Dict]:
        items = self._districts
        if zone:
            zk = _norm(zone)
            items = [d for d in items if _norm(d.zone_code) == zk or _norm(d.name_en).startswith(zk)]
        if province:
            pk = _norm(province)
            items = [d for d in items if _norm(d.province_code) == pk]
        if name_contains:
            n = _norm(name_contains)
            items = [d for d in items if n in _norm(d.name_en) or n in _norm(d.name_ne)]
        return [d.__dict__ for d in items]

    def get_district(self, code_or_name: str) -> Optional[Dict]:
        k = _norm(code_or_name)
        for d in self._districts:
            if _norm(d.code) == k or _norm(d.name_en) == k or _norm(d.name_ne) == k:
                return d.__dict__
        return None

    def get_place(self, slug_or_name: str) -> Optional[Dict]:
        k = _norm(slug_or_name)
        hit = self._places_by_slug.get(k)
        if hit:
            return hit.__dict__
        for p in self._places:
            if _norm(p.name_en) == k or _norm(p.name_ne) == k:
                return p.__dict__
        return None

    # --------------- ONE METHOD TO RULE THEM ALL ---------------

    def query_places(
        self,
        *,
        # filters
        province: Optional[str] = None,
        zone: Optional[str] = None,
        district: Optional[str] = None,
        tags_any: Optional[Iterable[str]] = None,
        tags_all: Optional[Iterable[str]] = None,
        famous_only: bool = False,
        # text search
        query: Optional[str] = None,
        # nearby filter
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius_km: Optional[float] = None,
        include_distance: bool = True,
        # sort + cap
        sort_by: str = "name",   # "distance" | "score" | "name"
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Unified query for places:
          - Filter: province / zone / district / tags_any / tags_all / famous_only
          - Search: query over slug/name_en/name_ne/alt_names (rank exact > prefix > contains)
          - Nearby: lat/lng within radius_km (Haversine), with optional 'km' in rows
          - Sort: "distance" (requires nearby), "score" (requires query), or "name" (default)
          - Limit: top N results
        """
        # Resolve province/zone codes (accepts names or codes)
        pcode = None
        if province:
            p = self.get_province(province)
            pcode = p["code"] if p else None

        zcode = None
        if zone:
            z = self.get_zone(zone)
            zcode = z["code"] if z else None

        dkey = _norm(district) if district else None

        tags_any_set = {t.strip().lower() for t in (tags_any or []) if t and t.strip()}
        tags_all_set = {t.strip().lower() for t in (tags_all or []) if t and t.strip()}

        def _ok_tags(tlist: List[str]) -> bool:
            tnorm = {t.lower().strip() for t in (tlist or [])}
            if tags_any_set and not (tnorm & tags_any_set):
                return False
            if tags_all_set and not tags_all_set.issubset(tnorm):
                return False
            return True

        # 1) Base filter pass
        pool: List[PlaceItem] = []
        for p in self._places:
            if famous_only and not getattr(p, "famous", False):
                continue
            if pcode and _norm(getattr(p, "province_code", "")) != _norm(pcode):
                continue
            if zcode and _norm(getattr(p, "zone_code", "")) != _norm(zcode):
                continue
            if dkey and _norm(getattr(p, "district_code", "")) != dkey:
                continue
            if not _ok_tags(getattr(p, "tags", [])):
                continue
            pool.append(p)

        # 2) Optional nearby filter (compute distance)
        rows_with_distance: List[Tuple[PlaceItem, Optional[float]]] = []
        have_nearby = lat is not None and lng is not None and radius_km is not None and radius_km > 0
        if have_nearby:
            for p in pool:
                plat, plng = getattr(p, "lat", None), getattr(p, "lng", None)
                if plat is None or plng is None:
                    continue
                dkm = _haversine_km(lat, lng, float(plat), float(plng))
                if dkm <= float(radius_km):
                    rows_with_distance.append((p, dkm))
        else:
            rows_with_distance = [(p, None) for p in pool]

        # 3) Optional search scoring
        q = _norm(query) if query else ""
        results_scored: List[Tuple[PlaceItem, Optional[float], float]] = []  # (place, km, score)
        if q:
            for p, dkm in rows_with_distance:
                score = 0.0
                fields = [
                    getattr(p, "slug", "") or "",
                    getattr(p, "name_en", "") or "",
                    getattr(p, "name_ne", "") or "",
                    *getattr(p, "alt_names", []),
                ]
                for f in fields:
                    fn = _norm(f)
                    if not fn:
                        continue
                    if fn == q:
                        score = max(score, 3.0)
                    elif fn.startswith(q):
                        score = max(score, 2.0)
                    elif q in fn:
                        score = max(score, 1.0)
                if score > 0:
                    results_scored.append((p, dkm, score))
        else:
            # no query → score = 0, but keep everyone
            results_scored = [(p, dkm, 0.0) for p, dkm in rows_with_distance]

        # 4) Sort
        if sort_by == "distance" and have_nearby:
            results_scored.sort(key=lambda t: (t[1] if t[1] is not None else float("inf"),
                                               _norm(getattr(t[0], "name_en", ""))))
        elif sort_by == "score" and q:
            results_scored.sort(key=lambda t: (-t[2], _norm(getattr(t[0], "name_en", ""))))
        else:
            # default: name
            results_scored.sort(key=lambda t: _norm(getattr(t[0], "name_en", "")))

        # 5) Shape output
        out: List[Dict] = []
        for p, dkm, score in results_scored:
            row = p.__dict__.copy()
            if include_distance and dkm is not None:
                row["km"] = round(dkm, 3)
            if q:
                row["score"] = score
            out.append(row)

        # 6) Cap
        if limit and limit > 0:
            out = out[:limit]
        return out

    # ------------------ ergonomic wrappers ------------------

    def list_places(self, **kwargs) -> List[Dict]:
        """List with filters, no text query, name-sorted by default."""
        kwargs.pop("query", None)
        kwargs.setdefault("sort_by", "name")
        return self.query_places(**kwargs)

    def nearby_places(self, lat: float, lng: float, **kwargs) -> List[Dict]:
        """Nearby + filters; default sort by distance when lat/lng/radius provided."""
        kwargs["lat"] = lat
        kwargs["lng"] = lng
        kwargs.setdefault("sort_by", "distance")
        if "radius_km" not in kwargs:
            kwargs["radius_km"] = 25.0
        return self.query_places(**kwargs)

    def list_famous_places(self, **kwargs) -> List[Dict]:
        """Famous-only helper (still supports all filters)."""
        kwargs["famous_only"] = True
        return self.query_places(**kwargs)
