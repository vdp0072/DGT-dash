from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import get_current_admin
from backend.models import UserData

# Mock admin dependency
async def mock_get_current_admin():
    return UserData(username="test_admin", role="admin")

app.dependency_overrides[get_current_admin] = mock_get_current_admin

client = TestClient(app)

def test_lookup_endpoint():
    print("Testing POST /api/lookup...")
    response = client.post(
        "/api/lookup",
        json={"phone": "919999999999"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "findings" in data
    assert "errors" in data
    assert data["phone"] == "919999999999"
    print("API Endpoint test passed!")

if __name__ == "__main__":
    try:
        test_lookup_endpoint()
    finally:
        # Clean up overrides
        app.dependency_overrides = {}
