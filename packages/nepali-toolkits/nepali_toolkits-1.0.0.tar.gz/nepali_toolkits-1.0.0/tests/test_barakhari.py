from nepali_toolkit.scripts.barakhari import table

print("Barakhari:", table(out="dev"))

print("Specific Base:", table(["ka", "kha"], out="dev"))