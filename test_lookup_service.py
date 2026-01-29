import sys
import os
import time

# Add parent dir to path if needed to find backend/phone_lookup
sys.path.append(os.getcwd())

from phone_lookup.service import lookup_single

def test():
    print("--- Starting verbose lookup test ---")
    start_time = time.time()
    
    # Using a known number that might trigger some output
    findings, errors = lookup_single("919999999999")
    
    end_time = time.time()
    print(f"Test completed in {end_time - start_time:.2f} seconds")
    
    print("\n--- FINDINGS ---")
    for prov, val in findings.items():
        print(f"[{prov}]: {val[:100]}...") # Print first 100 chars
        
    print("\n--- ERRORS ---")
    for prov, err in errors.items():
        print(f"[{prov}]: {err}")
    
    # Assert return types
    assert isinstance(findings, dict)
    assert isinstance(errors, dict)
    print("\nValidation: Response types are correct.")

if __name__ == "__main__":
    test()
