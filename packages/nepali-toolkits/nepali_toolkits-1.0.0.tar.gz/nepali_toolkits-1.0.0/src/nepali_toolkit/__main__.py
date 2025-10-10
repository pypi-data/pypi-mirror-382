import argparse, json
from nepali_toolkit.core import NepaliToolkit
from nepali_toolkit.common.i18n import to_ne_digits

def _emit(x, fmt="table", ne_digits=False):
    if fmt == "json":
        s = json.dumps(x, ensure_ascii=False, indent=2)
        print(to_ne_digits(s) if ne_digits else s)
    else:
        if isinstance(x, list):
            for r in x: print(to_ne_digits(r) if ne_digits else r)
        else: print(to_ne_digits(x) if ne_digits else x)

def cli():
    tk = NepaliToolkit()

    p = argparse.ArgumentParser("nepali-toolkit")
    p.add_argument("-f","--format", choices=["table","json"], default="table")
    p.add_argument("--ne-digits", action="store_true", help="Show Nepali digits (०१२…)")
    sub = p.add_subparsers(dest="cmd", required=True)

    # bs
    p_bs = sub.add_parser("bs")
    sbs = p_bs.add_subparsers(dest="bscmd", required=True)
    sbs.add_parser("now")
    tobs = sbs.add_parser("to-bs"); tobs.add_argument("ad_date")
    toad = sbs.add_parser("to-ad"); toad.add_argument("bs_date")
    hol = sbs.add_parser("holidays"); hol.add_argument("bs_year", type=int)

    # script
    p_sc = sub.add_parser("script")
    ssc = p_sc.add_subparsers(dest="scmd", required=True)
    tr = ssc.add_parser("translit"); tr.add_argument("text"); tr.add_argument("--dir", choices=["roman2ne","ne2roman"], default="roman2ne")
    bk = ssc.add_parser("barakhari"); bk.add_argument("consonant")

    # admin
    p_ad = sub.add_parser("admin")
    sad = p_ad.add_subparsers(dest="acmd", required=True)

    # lists
    sad.add_parser("provinces")
    sad.add_parser("zones")

    ld = sad.add_parser("districts")
    ld.add_argument("--zone", default=None, help="Legacy zone code or name (e.g. Bagmati)")
    ld.add_argument("--province", default=None, help="Province code (e.g. P3)")
    ld.add_argument("--name", dest="name_contains", default=None, help="Substring in English/Nepali name")

    # places: either by zone OR search text
    lpz = sad.add_parser("places")
    grp = lpz.add_mutually_exclusive_group(required=True)
    grp.add_argument("--zone", help="Legacy zone code (e.g. Bagmati)")
    grp.add_argument("--search", help="Search text for places (e.g. 'patan')")
    lpz.add_argument("--limit", type=int, default=20)

    # gazetteer
    p_gz = sub.add_parser("famous")
    sgz = p_gz.add_subparsers(dest="gcmd", required=True)
    ffind = sgz.add_parser("find"); ffind.add_argument("query"); ffind.add_argument("--limit", type=int, default=5)
    fnear = sgz.add_parser("nearby"); fnear.add_argument("lat", type=float); fnear.add_argument("lng", type=float); fnear.add_argument("--radius", type=float, default=25.0)

    # units
    p_un = sub.add_parser("units")
    sun = p_un.add_subparsers(dest="ucmd", required=True)
    sun.add_parser("to-m2").add_argument("text")
    sun.add_parser("to-l").add_argument("text")
    um = sun.add_parser("to-kg"); um.add_argument("text"); um.add_argument("--commodity", default="rice")

    a = p.parse_args(); fmt=a.format; nep=a.ne_digits

    if a.cmd == "bs":
        if a.bscmd == "now": _emit(str(tk.bs.today_bs()), fmt, nep)
        elif a.bscmd == "to-bs": _emit(str(tk.bs.to_bs(a.ad_date)), fmt, nep)
        elif a.bscmd == "to-ad": _emit(str(tk.bs.to_ad(a.bs_date)), fmt, nep)
        else: _emit(tk.holidays.list_for_year(a.bs_year), fmt, nep)

    elif a.cmd == "script":
        if a.scmd == "translit":
            _emit(tk.script.roman_to_dev(a.text) if a.dir=="roman2ne" else tk.script.dev_to_roman(a.text), fmt, nep)
        else:
            tbl = tk.barakhari.table(a.consonant)
            _emit("\n".join([" ".join(row) for row in tbl]), fmt, nep)

    elif a.cmd == "admin":
        if a.acmd == "provinces": _emit(tk.admin.list_provinces(), fmt, nep)
        elif a.acmd == "zones": _emit(tk.admin.list_zones(), fmt, nep)
        elif a.acmd == "districts": _emit(tk.admin.list_districts(zone=a.zone), fmt, nep)
        else: _emit(tk.admin.places_by_zone(a.zone), fmt, nep)

    elif a.cmd == "famous":
        if a.gcmd == "find":
            res = [{"slug": p.slug, "name_en": p.name_en, "score": s} for p,s in tk.gazetteer.search(a.query, limit=a.limit)]
            _emit(res, fmt, nep)
        else:
            res = [{"slug": p.slug, "name_en": p.name_en, "km": round(d,1)} for p,d in tk.gazetteer.nearby(a.lat, a.lng, radius_km=a.radius)]
            _emit(res, fmt, nep)

    else:  # units
        if a.ucmd == "to-m2": _emit({"m2": tk.units.area_m2(a.text)}, fmt, nep)
        elif a.ucmd == "to-l": _emit({"L": tk.units.volume_l(a.text)}, fmt, nep)
        else: _emit({"kg": tk.units.mass_kg(a.text, commodity=a.commodity)}, fmt, nep)

if __name__ == "__main__":
    cli()
