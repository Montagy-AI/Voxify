import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/v1"

def test_auth():
    # Register
    register_data = {
        "email": "test@example.com",
        "password": "Test123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print("\n1. Testing Registration:")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Login
    login_data = {
        "email": "test@example.com",
        "password": "Test123!"
    }
    
    print("\n2. Testing Login:")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    return None

def test_samples(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test list samples
    print("\n3. Testing List Voice Samples:")
    response = requests.get(f"{BASE_URL}/voice/samples", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("Starting API Tests...")
    token = test_auth()
    if token:
        test_samples(token)
    else:
        print("Authentication failed. Cannot proceed with voice sample tests.") 