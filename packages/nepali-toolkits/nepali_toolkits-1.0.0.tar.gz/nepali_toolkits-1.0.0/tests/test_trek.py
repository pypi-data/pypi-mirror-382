from nepali_toolkit.trek import list_treks, search_treks, nearby_treks, get_trek, query_treks, suggest

print(len(list_treks()))
print(get_trek("annapurna-circuit"))

print(search_treks("everest", difficulty=["moderate","hard"], limit=5))
print(nearby_treks(27.7172, 85.3240, radius_km=120))  # around Kathmandu
print(query_treks(provinces=["P1","P3"], days_max=10, sort_by="days"))
print(suggest("anna"))
