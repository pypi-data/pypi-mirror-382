from importlib.resources import files
import json, re, unicodedata
from functools import lru_cache

@lru_cache(maxsize=None)
def read_json_resource(pkg: str, path: str):
    p = files(pkg) / path
    return json.loads(p.read_text(encoding="utf-8"))

def slugify_en(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii","ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "item"
