from _bootstrap import ok, check
from nepali_toolkit.bs import to_bs, to_ad, today_bs, now
# from nepali_toolkit.bs import to_ad

print("\n=== AD → BS ===")
bs_obj = to_bs("1999-10-01")
print("Raw BS (ISO):", str(bs_obj))
print("EN label:    ", to_bs("1999-10-01", fmt="YYYY MMM D", lang="en"))
print("NE label:    ", to_bs("1999-10-01", fmt="YYYY MMMM DD", lang="ne", ne_digits=True))




print("\n=== BS → AD ===")
ad_obj = to_ad("2056-06-14")
print("Raw AD (ISO):", ad_obj.isoformat())
print("EN label:    ", to_ad("2056-06-14", fmt="YYYY MMM D", lang="en"))
print("NE label:    ", to_ad("2056-06-14", fmt="YYYY MMMM DD", lang="ne", ne_digits=True))


print("\n=== TODAY (BS) ===")
bs_obj = today_bs()
print("Raw BS (ISO)      :", str(bs_obj))
print("EN (space style)  :", today_bs(fmt="YYYY MMM D", lang="en"))
print("NE (full+digits)  :", today_bs(fmt="YYYY MMMM DD", lang="ne", ne_digits=True))


print("\n=== NOW (BS + AD) ===")
bs_now, dt_now = now()
print("Now BS (ISO)      :", str(bs_now))
print("Now AD (ISO)      :", dt_now.isoformat())


bs_now_en, dt_now_en = now(fmt="YYYY MMM D", lang="en")
print("Now BS (EN)       :", bs_now_en)


bs_now_ne, dt_now_ne = now(fmt="YYYY MMMM DD", lang="ne", ne_digits=True)
print("Now BS (NE)       :", bs_now_ne)


ok("BS manual checks ran")
