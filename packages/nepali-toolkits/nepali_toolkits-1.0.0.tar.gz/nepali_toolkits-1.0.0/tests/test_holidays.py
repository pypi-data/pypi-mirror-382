from nepali_toolkit.holiday import list_holiday, next_holiday, list_holiday_between

print("Festival (current year):", list_holiday(tags=["festival"]))

print("Festival in Ashwin:", list_holiday(tags=["festival"], month=6))

print("Public 2082:", list_holiday(2082, tags=["public"]))

print("Search Holidays:", list_holiday(limit=5))

print("Next Holiday:", next_holiday(bs_from="2081-06-15", limit=20))

print("List Holiday Between:", list_holiday_between("2081-06-15", "2082-06-20", tags=["festival"]))