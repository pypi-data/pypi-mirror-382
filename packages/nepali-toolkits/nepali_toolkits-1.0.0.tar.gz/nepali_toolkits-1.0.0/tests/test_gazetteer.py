from nepali_toolkit.gazetteer import list_provinces, list_zones, get_zone, list_districts, list_places, get_place, get_district, get_province, nearby_places


print("Provinces:", list_provinces())
print("Zones:", list_zones())
print("Zone (Bagmati):", get_zone("Bagmati"))
print("Districts in Bagmati zone:", list_districts())
print("Districts in Bagmati zone:", list_districts(zone="Bagmati"))



print("Places in Bagmati zone (first 10):", list_places(zone="Bagmati", limit=10))


print("Search districts containing 'kathmandu':",list_districts(name_contains="kathmandu"))

print("Place by slug 'biratnagar':", get_place("biratnagar"))

print("District by code 'KTM':", get_district("KTM"))

print("Province by code 'P3':", get_province("P3"))

print("Nearby famous (≤5km of Thamel):",nearby_places(27.6711, 85.4298, radius_km=5, famous_only=True, limit=10))
