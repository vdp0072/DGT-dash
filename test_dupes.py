
import requests
import sqlite3

BASE_URL = "http://127.0.0.1:8000/api"

def test_duplicates():
    # 1. Login Admin
    print("1. Logging in as Admin...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    admin_token = resp.json()["access_token"]
    headers = {'Authorization': f"Bearer {admin_token}"}

    # 2. Ingest Data with Duplicates
    print("2. Ingesting Data with Duplicates...")
    csv_content = """name,phone,city
    DupTest,5555555555,CityA
    DupTest,5555555555,CityA
    NewUser,1234567890,CityB
    """.strip()
    
    files = {'file': ('dupes.csv', csv_content, 'text/csv')}
    resp = requests.post(f"{BASE_URL}/admin/ingest", files=files, headers=headers)
    data = resp.json()
    print("   Ingest Result (First time):", data)
    # Expected: Total: 3, Inserted: 2, Rejected: 1 (if NewUser didn't exist)
    # Wait, if NewUser already existed from a previous run, it might be different.
    # Let's check the numbers.

    # 3. Ingest same data again
    print("3. Ingesting same data again...")
    files = {'file': ('dupes.csv', csv_content, 'text/csv')}
    resp = requests.post(f"{BASE_URL}/admin/ingest", files=files, headers=headers)
    data = resp.json()
    print("   Ingest Result (Second time):", data)
    # Expected: Total: 3, Inserted: 0, Rejected: 3

    # 4. Search to confirm
    print("4. Searching to confirm counts...")
    resp = requests.get(f"{BASE_URL}/search?q=DupTest", headers=headers)
    results = resp.json()["results"]
    print(f"   Found {len(results)} records for 'DupTest'. (Expected: 1)")
    
    if len(results) == 1:
        print("   SUCCESS: Deduplication working at ingestion time!")
    else:
        print(f"   FAILURE: Found {len(results)} records instead of 1.")

if __name__ == "__main__":
    test_duplicates()
