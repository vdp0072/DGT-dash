from phone_lookup.service import lookup_single
import json

phone = "917350272282"
print(f"Starting lookup for {phone}...")
findings, errors = lookup_single(phone)

print("\n--- FINDINGS ---")
for k, v in findings.items():
    print(f"[{k}]:")
    print(v)
    print("-" * 20)

print("\n--- ERRORS ---")
print(json.dumps(errors, indent=2))
