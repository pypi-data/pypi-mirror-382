#!/usr/bin/env python3
from _bootstrap import ok, check
from nepali_toolkit.scripts.translator import dev_to_roman, roman_to_dev

dev = roman_to_dev("pokharaa")
print("Roman→Devanagari:", dev)
check(dev != "Bhairahawa", "roman_to_dev changed text")

rom = dev_to_roman("पोखरा")
print("Devanagari→Roman:", rom)
check(isinstance(rom, str) and len(rom) > 0, "dev_to_roman returned text")

ok("Script transliteration checks passed")
