from __future__ import annotations
from typing import List, Dict, Optional, Iterable, Tuple
from importlib.resources import files
import json
import math

from nepali_toolkit.common.util import read_json_resource
from .models import TrekRoute

# ---------------- helpers ----------------

def _norm(s: str) -> str:
    return (s or "").casefold().strip()

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# -------------- main service -------------

class TrekCatalog:

    def __init__(self):
        rows = read_json_resource("nepali_toolkit.trek.data", "treks.json")
        self._treks: List[TrekRoute] = [TrekRoute.from_dict(r) for r in rows]
        self._by_slug: Dict[str, TrekRoute] = { _norm(t.slug): t for t in self._treks }

    # -------- basic ------------

    def list_treks(self) -> List[Dict]:
        return [t.to_dict() for t in self._treks]

    def get_trek(self, slug_or_name: str) -> Optional[Dict]:
        k = _norm(slug_or_name)
        hit = self._by_slug.get(k)
        if hit:
            return hit.to_dict()
        for t in self._treks:
            if _norm(t.name_en) == k or _norm(t.name_ne) == k:
                return t.to_dict()
        return None

    # -------- unified query ----

    def query_treks(
        self,
        *,
        # filters
        provinces: Optional[Iterable[str]] = None,
        districts: Optional[Iterable[str]] = None,
        region_contains: Optional[str] = None,
        difficulty: Optional[Iterable[str]] = None,     # e.g. ["easy","moderate"]
        permit_any: Optional[Iterable[str]] = None,
        permit_all: Optional[Iterable[str]] = None,
        tags_any: Optional[Iterable[str]] = None,
        tags_all: Optional[Iterable[str]] = None,
        seasons_any: Optional[Iterable[str]] = None,
        days_min: Optional[int] = None,
        days_max: Optional[int] = None,
        alt_min: Optional[int] = None,                  # filter by max_alt_m >= alt_min
        alt_max: Optional[int] = None,                  # and/or max_alt_m <= alt_max
        # text search
        query: Optional[str] = None,
        # nearby
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius_km: Optional[float] = None,              # if provided, filter by start point within radius
        include_distance: bool = True,
        # sort/limit
        sort_by: str = "name",                          # "distance" | "score" | "name" | "days" | "alt"
        limit: Optional[int] = None,
    ) -> List[Dict]:

        prov_set = { _norm(p) for p in (provinces or []) if p }
        dist_set = { _norm(d) for d in (districts or []) if d }
        reg_needle = _norm(region_contains) if region_contains else None
        diff_set = { _norm(d) for d in (difficulty or []) if d }

        perm_any = { _norm(p) for p in (permit_any or []) if p }
        perm_all = { _norm(p) for p in (permit_all or []) if p }
        tags_any_set = { _norm(t) for t in (tags_any or []) if t }
        tags_all_set = { _norm(t) for t in (tags_all or []) if t }
        seasons_any_set = { _norm(s) for s in (seasons_any or []) if s }

        # 1) base filter
        pool: List[TrekRoute] = []
        for t in self._treks:
            if prov_set and not (set(map(_norm, t.provinces)) & prov_set):
                continue
            if dist_set and not (set(map(_norm, t.districts)) & dist_set):
                continue
            if reg_needle and (reg_needle not in _norm(t.region)):
                continue
            if diff_set and _norm(t.difficulty) not in diff_set:
                continue
            if days_min is not None and (t.days or 0) < int(days_min):
                continue
            if days_max is not None and (t.days or 1_000) > int(days_max):
                continue
            if alt_min is not None and (t.max_alt_m or 0) < int(alt_min):
                continue
            if alt_max is not None and (t.max_alt_m or 1_000_000) > int(alt_max):
                continue

            # permits/tag/seasons
            tperm = { _norm(p) for p in (t.permits or []) }
            if perm_any and not (tperm & perm_any):     # any-of
                continue
            if perm_all and not perm_all.issubset(tperm):
                continue

            ttags = { _norm(x) for x in (t.tags or []) }
            if tags_any_set and not (ttags & tags_any_set):
                continue
            if tags_all_set and not tags_all_set.issubset(ttags):
                continue

            tseasons = { _norm(s) for s in (t.seasons or []) }
            if seasons_any_set and not (tseasons & seasons_any_set):
                continue

            pool.append(t)

        # 2) nearby filter on START point
        with_dist: List[Tuple[TrekRoute, Optional[float]]] = []
        have_nearby = lat is not None and lng is not None and radius_km is not None and radius_km > 0
        if have_nearby:
            for t in pool:
                if t.start_lat is None or t.start_lng is None:
                    continue
                dkm = _haversine_km(lat, lng, float(t.start_lat), float(t.start_lng))
                if dkm <= float(radius_km):
                    with_dist.append((t, dkm))
        else:
            with_dist = [(t, None) for t in pool]

        # 3) search scoring
        q = _norm(query) if query else ""
        scored: List[Tuple[TrekRoute, Optional[float], float]] = []
        if q:
            for t, dkm in with_dist:
                score = 0.0
                fields = [
                    t.slug,
                    t.name_en,
                    t.name_ne or "",
                    t.region or "",
                    *t.highlights,
                    *t.tags,
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
                    scored.append((t, dkm, score))
        else:
            scored = [(t, dkm, 0.0) for t, dkm in with_dist]

        # 4) sort
        if sort_by == "distance" and have_nearby:
            scored.sort(key=lambda x: (x[1] if x[1] is not None else float("inf"), _norm(x[0].name_en)))
        elif sort_by == "score" and q:
            scored.sort(key=lambda x: (-x[2], _norm(x[0].name_en)))
        elif sort_by == "days":
            scored.sort(key=lambda x: (x[0].days or 0, _norm(x[0].name_en)))
        elif sort_by == "alt":
            scored.sort(key=lambda x: (x[0].max_alt_m or 0, _norm(x[0].name_en)))
        else:
            scored.sort(key=lambda x: _norm(x[0].name_en))

        # 5) shape
        out: List[Dict] = []
        for t, dkm, score in scored:
            row = t.to_dict()
            if include_distance and dkm is not None:
                row["km"] = round(dkm, 3)
            if q:
                row["score"] = score
            out.append(row)

        if limit and limit > 0:
            out = out[:limit]
        return out

    # ---------- ergonomic helpers ----------

    def search_treks(self, query: str, **kwargs) -> List[Dict]:
        kwargs["query"] = query
        kwargs.setdefault("sort_by", "score")
        return self.query_treks(**kwargs)

    def nearby_treks(self, lat: float, lng: float, **kwargs) -> List[Dict]:
        kwargs["lat"] = lat
        kwargs["lng"] = lng
        kwargs.setdefault("radius_km", 50.0)
        kwargs.setdefault("sort_by", "distance")
        return self.query_treks(**kwargs)

    def suggest(self, prefix: str, *, limit: int = 8, kinds: Optional[Iterable[str]] = None) -> List[Dict]:
        """
        Simple autocomplete by slug/name_en/name_ne/region/tags/highlights.
        """
        p = _norm(prefix)
        if not p:
            return []
        results: List[Tuple[Dict, float]] = []
        for t in self._treks:
            fields = [t.slug, t.name_en, t.name_ne or "", t.region or "", *t.tags, *t.highlights]
            top = 0.0
            for f in fields:
                fn = _norm(f)
                if not fn:
                    continue
                if fn.startswith(p):
                    top = max(top, 2.0)
                elif p in fn:
                    top = max(top, 1.0)
            if top > 0:
                results.append(({"slug": t.slug, "name_en": t.name_en}, top))
        results.sort(key=lambda t: (-t[1], _norm(t[0]["name_en"])))
        return [r for r, _ in results[:max(1, limit)]]
