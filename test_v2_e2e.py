
import requests
import sqlite3
from passlib.context import CryptContext

DB_PATH = "d:/DGT_dash/dgt.db"
BASE_URL = "http://127.0.0.1:8000/api"

def test_flow():
    # 1. Login Admin
    print("1. Logging in as Admin...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    if resp.status_code != 200:
        print("FAILED LOGIN:", resp.text)
        return
    admin_token = resp.json()["access_token"]
    print("   Success. Token received.")

    # 2. Ingest Data (with Father's Name)
    print("2. Ingesting Data...")
    csv_content = """name,fathers_name,age,gender,city,constituency,phone,misc
    Alice,John Doe,30,F,Metro,Central,9998887777,SecretData
    Bob,Jane Doe,45,M,Metro,North,1112223333,
    """.strip()
    
    files = {'file': ('test_v2.csv', csv_content, 'text/csv')}
    headers = {'Authorization': f"Bearer {admin_token}"}
    
    resp = requests.post(f"{BASE_URL}/admin/ingest", files=files, headers=headers)
    if resp.status_code != 200:
         print("FAILED INGEST:", resp.text)
    else:
         print("   Ingest Result:", resp.json())

    # 3. Search as Admin
    print("3. Search as Admin...")
    resp = requests.get(f"{BASE_URL}/search?q=Alice", headers=headers)
    data = resp.json()
    print(f"   Found {len(data['results'])} records.")
    if len(data['results']) > 0:
        rec = data['results'][0]
        print("   Sample:", rec)
        # Verify raw phone and father's name are visible
        if rec['fathers_name'] != "John Doe":
             print("   ERROR: Father's name mismatch!")
        if '****' in rec['phone']:
             print("   ERROR: Admin should see raw phone!")
        else:
             print("   Verified: Admin sees raw data.")

    # 4. Search as Demo User (role: user)
    print("4. Logging in as Demo User...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "demo", "password": "demo123"})
    if resp.status_code != 200:
        print("FAILED DEMO LOGIN:", resp.text)
        return
    user_token = resp.json()["access_token"]
    
    print("5. Search as Demo User...")
    user_headers = {'Authorization': f"Bearer {user_token}"}
    resp = requests.get(f"{BASE_URL}/search?q=Alice", headers=user_headers)
    data = resp.json()
    if len(data['results']) > 0:
        rec = data['results'][0]
        print("   Sample:", rec)
        # Verify masking
        if '****' not in rec['phone']:
             print("   ERROR: User should see masked phone!")
        elif rec['misc'] != "PROTECTED":
             print("   ERROR: Misc field not protected!")
        else:
             print("   Verified: Demo user sees masked data but father's name is visible.")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print("Test failed with exception:", e)
