import json
import time
import random
import sys
try:
    from .service import lookup_single
except (ImportError, ValueError):
    from service import lookup_single

def process_lookups():
    input_file = 'rows_13000_13500_processed.json'
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return
    
    total = len(data)
    processed_in_this_run = 0
    
    for i, record in enumerate(data, start=1):
        if 'result' in record and record['result']:
            continue
            
        phone = str(record.get('mob_ind'))
        print(f"[{i}/{total}] Processing: {phone}")
        
        # Batch safety cooldown
        processed_in_this_run += 1
        if processed_in_this_run > 1 and processed_in_this_run % 50 == 0:
            print("Cooldown (20s)...")
            time.sleep(20)
            
        # Call the decoupled service
        findings, errors = lookup_single(phone)
        
        # Format results as a string for the JSON record (legacy compatibility)
        # We'll join findings with '|' and also note errors if any
        res_parts = []
        for prov, val in findings.items():
            res_parts.append(f"{prov}: {val}")
        
        for prov, err in errors.items():
            res_parts.append(f"[{prov} ERROR]: {err}")
            
        record['result'] = " | ".join(res_parts)
        
        # Save every 10 records for safety
        if processed_in_this_run % 10 == 0:
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"--- Checkpoint: Saved up to record {i} ---")

        # Regular random delay to avoid rate limits
        delay = random.uniform(1.5, 2.5)
        time.sleep(delay)
            
    # Final save
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    print(f"\nSuccessfully processed all {total} records.")

if __name__ == "__main__":
    process_lookups()
