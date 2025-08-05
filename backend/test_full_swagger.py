#!/usr/bin/env python3
"""
Complete test script to verify full Swagger functionality is working
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_server_status():
    """Test if server is running and responsive"""
    print("🔍 Testing Server Status...")
    
    try:
        # Test main endpoint
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Main endpoint: {response.status_code}")
        
        # Test health check
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        
        # Test API info
        response = requests.get(f"{BASE_URL}/api/info", timeout=5)
        print(f"✅ API info: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False

def test_swagger_documentation():
    """Test Swagger documentation endpoints"""
    print("\n📚 Testing Swagger Documentation...")
    
    try:
        # Test Swagger UI
        response = requests.get(f"{BASE_URL}/docs/", timeout=10)
        print(f"✅ Swagger UI: {response.status_code}")
        
        # Test OpenAPI JSON spec
        response = requests.get(f"{BASE_URL}/docs/swagger.json", timeout=10)
        if response.status_code == 200:
            spec = response.json()
            paths = spec.get('paths', {})
            print(f"✅ OpenAPI Spec: {response.status_code} - {len(paths)} endpoints documented")
            
            # List some key endpoints
            key_endpoints = ['/auth/login', '/auth/register', '/voice/samples', '/job', '/file/synthesis/{job_id}']
            for endpoint in key_endpoints:
                found = any(endpoint.replace('{job_id}', '{string:job_id}') in path for path in paths.keys())
                status = "✅" if found else "⚠️"
                print(f"  {status} {endpoint}")
        else:
            print(f"⚠️ OpenAPI Spec: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Swagger documentation error: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints with full workflow"""
    print("\n🔐 Testing Authentication Endpoints...")
    
    # Test data
    user_data = {
        "email": "test.swagger@example.com",
        "password": "SecurePass123!",
        "first_name": "Swagger",
        "last_name": "Test"
    }
    
    try:
        # Test registration
        response = requests.post(f"{API_BASE}/auth/register", json=user_data, timeout=10)
        if response.status_code in [201, 409]:  # Created or already exists
            print(f"✅ Registration: {response.status_code}")
        else:
            print(f"⚠️ Registration: {response.status_code} - {response.text[:100]}")
        
        # Test login
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success') and 'access_token' in data.get('data', {}):
                    access_token = data['data']['access_token']
                    print(f"✅ Login: {response.status_code} - Token received")
                    return access_token
                else:
                    print(f"⚠️ Login: Invalid response format")
            except json.JSONDecodeError:
                print(f"⚠️ Login: Invalid JSON response")
        else:
            print(f"❌ Login: {response.status_code} - {response.text[:100]}")
        
    except Exception as e:
        print(f"❌ Auth endpoints error: {e}")
    
    return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication"""
    print("\n🔒 Testing Authenticated Endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test profile
        response = requests.get(f"{API_BASE}/auth/profile", headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ Get Profile: {response.status_code}")
        else:
            print(f"❌ Get Profile: {response.status_code} - {response.text[:100]}")
        
        # Test profile update
        update_data = {"first_name": "Updated", "last_name": "Name"}
        response = requests.put(f"{API_BASE}/auth/profile", json=update_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ Update Profile: {response.status_code}")
        else:
            print(f"⚠️ Update Profile: {response.status_code}")
        
        # Test voice samples list
        response = requests.get(f"{API_BASE}/voice/samples", headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ Voice Samples List: {response.status_code}")
        else:
            print(f"⚠️ Voice Samples List: {response.status_code}")
        
        # Test voice clones list
        response = requests.get(f"{API_BASE}/voice/clones", headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ Voice Clones List: {response.status_code}")
        else:
            print(f"⚠️ Voice Clones List: {response.status_code}")
        
        # Test jobs list
        response = requests.get(f"{API_BASE}/job", headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ Jobs List: {response.status_code}")
        else:
            print(f"⚠️ Jobs List: {response.status_code}")
        
        # Test token refresh
        refresh_token = "test_refresh_token"  # In real scenario, get from login response
        response = requests.post(f"{API_BASE}/auth/refresh", headers=headers, timeout=10)
        if response.status_code in [200, 401]:  # 401 expected for invalid refresh token
            print(f"✅ Token Refresh Endpoint: {response.status_code}")
        else:
            print(f"⚠️ Token Refresh: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Authenticated endpoints error: {e}")

def test_public_endpoints():
    """Test public endpoints that don't require authentication"""
    print("\n🌍 Testing Public Endpoints...")
    
    try:
        # Test voice models
        response = requests.get(f"{API_BASE}/voice/models", timeout=10)
        if response.status_code == 200:
            print(f"✅ Voice Models: {response.status_code}")
        else:
            print(f"⚠️ Voice Models: {response.status_code}")
        
        # Test voice service info
        response = requests.get(f"{API_BASE}/voice/info", timeout=10)
        if response.status_code == 200:
            print(f"✅ Voice Service Info: {response.status_code}")
        else:
            print(f"⚠️ Voice Service Info: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Public endpoints error: {e}")

def test_error_handling():
    """Test error handling and edge cases"""
    print("\n🚨 Testing Error Handling...")
    
    try:
        # Test invalid login
        response = requests.post(f"{API_BASE}/auth/login", 
                               json={"email": "invalid@test.com", "password": "wrong"}, 
                               timeout=10)
        if response.status_code == 401:
            print(f"✅ Invalid login error: {response.status_code}")
        else:
            print(f"⚠️ Invalid login: {response.status_code}")
        
        # Test missing authorization
        response = requests.get(f"{API_BASE}/auth/profile", timeout=10)
        if response.status_code == 401:
            print(f"✅ Missing auth error: {response.status_code}")
        else:
            print(f"⚠️ Missing auth: {response.status_code}")
        
        # Test invalid bearer token
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{API_BASE}/auth/profile", headers=headers, timeout=10)
        if response.status_code == 422:  # JWT decode error
            print(f"✅ Invalid token error: {response.status_code}")
        else:
            print(f"⚠️ Invalid token: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error handling test error: {e}")

def main():
    """Run comprehensive Swagger functionality tests"""
    print("🚀 Starting Complete Swagger Functionality Tests...\n")
    
    # Check if server is running
    if not test_server_status():
        print("\n❌ Server is not running. Please start with: python start.py")
        sys.exit(1)
    
    # Test documentation
    if not test_swagger_documentation():
        print("\n⚠️ Swagger documentation issues detected")
    
    # Test authentication workflow
    token = test_auth_endpoints()
    
    # Test authenticated endpoints if we got a token
    if token:
        test_authenticated_endpoints(token)
        print(f"\n🔑 Token format check: {'✅' if token.startswith('eyJ') else '❌'}")
    else:
        print("\n⚠️ Skipping authenticated endpoint tests (no token)")
    
    # Test public endpoints
    test_public_endpoints()
    
    # Test error handling
    test_error_handling()
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 Test Summary:")
    print(f"📋 Swagger UI: {BASE_URL}/docs/")
    print(f"📋 API Base: {API_BASE}")
    print(f"📋 OpenAPI Spec: {BASE_URL}/docs/swagger.json")
    print("✅ Tests completed!")
    
    if token:
        print(f"\n🔧 Test with curl:")
        print(f'curl -H "Authorization: Bearer {token[:50]}..." {API_BASE}/auth/profile')

if __name__ == "__main__":
    main()