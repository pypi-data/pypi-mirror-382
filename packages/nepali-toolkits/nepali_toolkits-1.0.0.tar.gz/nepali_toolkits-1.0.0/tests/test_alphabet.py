from nepali_toolkit.scripts.alphabet import vowel_alphabet, consonant_alphabet

print("Vowel Letters:", vowel_alphabet(out="dev", example=False))
print("Vowel Letters:", vowel_alphabet(out="roman", example=False))
print("Vowel Letters:", vowel_alphabet(out="pair", example=False))


print("Vowel Letters with examples:", vowel_alphabet(out="dev", example=True))
print("Vowel Letters with examples:", vowel_alphabet(out="roman", example=True))
print("Vowel Letters with examples:", vowel_alphabet(out="pair", example=True))


print("Consonant Letters:", consonant_alphabet(out="dev"))
print("Consonant Letters:", consonant_alphabet(out="roman"))
print("Consonant Letters:", consonant_alphabet(out="pair"))


print("Consonant Letters with examples:", consonant_alphabet(out="dev", example=True))
print("Consonant Letters with examples:", consonant_alphabet(out="roman", example=True))
print("Consonant Letters with examples:", consonant_alphabet(out="pair", example=True))


