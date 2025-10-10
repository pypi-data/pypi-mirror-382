# demo_named_args.py
from nepali_toolkit.units import convert


conv = convert  # shorthand

print("=== AREA (your profile: m & km are AREA shorthands: m², km²) ===")
print("1 m   -> km :", conv(1, from_unit="m",  to_unit="km"))   # 1e-6 (m² -> km²)
print("1 km  -> m  :", conv(1, from_unit="km", to_unit="m"))    # 1e6  (km² -> m²)

print("\n=== AREA (Nepali & metric) ===")
print("1 ropani -> bigha :",  conv(1, from_unit="ropani",  to_unit="bigha"))   # ~0.0751
print("1 bigha  -> dhur  :",  conv(1, from_unit="bigha",   to_unit="dhur"))    # 400
print("1 hectare-> aana  :",  conv(1, from_unit="hectare", to_unit="aana"))    # ~314.58

print("\n=== VOLUME ===")
print("2 pathi  -> liter :",  conv(2,   from_unit="pathi", to_unit="liter"))   # ~9.092176
print("500 ml   -> mana  :",  conv(500, from_unit="ml",    to_unit="mana"))    # ~0.8796

print("\n=== MASS ===")
print("5 tola   -> kg    :",  conv(5,   from_unit="tola",  to_unit="kg"))      # ~0.058319
print("2 lb     -> tola  :",  conv(2,   from_unit="lb",    to_unit="tola"))    # ~77.6
print("100 g    -> masha :",  conv(100, from_unit="g",     to_unit="masha"))   # ~102.9

print("\n=== ERROR CASES (Category mismatch) ===")
try:
    print("ropani -> kg:", conv(1, from_unit="ropani", to_unit="kg"))
except Exception as e:
    print("ropani -> kg ERROR:", e)

try:
    print("liter  -> bigha:", conv(1, from_unit="liter", to_unit="bigha"))
except Exception as e:
    print("liter  -> bigha ERROR:", e)

print("\n=== YOUR EXACT LINE ===")
print(conv(1, from_unit="km", to_unit="m"))  # with your current profile: AREA km² -> m² => 1000000.0
