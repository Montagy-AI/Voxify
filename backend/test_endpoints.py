import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000/api/v1"

def test_auth():
    # Register a test user
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
    
    # Login to get access token
    print("\n2. Testing Login:")
    login_data = {
        "email": "test@example.com",
        "password": "Test123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    return None

def test_voice_samples(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test upload
    print("\n3. Testing Voice Sample Upload:")
    # Get the path to test.wav in the project root
    test_wav_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test.wav')
    
    files = {
        'file': ('test.wav', open(test_wav_path, 'rb'), 'audio/wav'),
        'name': (None, 'Test Sample')
    }
    response = requests.post(f"{BASE_URL}/voice/samples", headers=headers, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        sample_id = response.json()["data"]["sample_id"]
        
        # Test get sample
        print("\n4. Testing Get Voice Sample:")
        response = requests.get(f"{BASE_URL}/voice/samples/{sample_id}", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test list samples
        print("\n5. Testing List Voice Samples:")
        response = requests.get(f"{BASE_URL}/voice/samples", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test delete sample
        print("\n6. Testing Delete Voice Sample:")
        response = requests.delete(f"{BASE_URL}/voice/samples/{sample_id}", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("Starting API Tests...")
    token = test_auth()
    if token:
        test_voice_samples(token)
    else:
        print("Authentication failed. Cannot proceed with voice sample tests.") 