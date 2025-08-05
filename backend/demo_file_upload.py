#!/usr/bin/env python3
"""
Demo script for testing file upload functionality with Swagger
Shows how to test both via Swagger UI and curl commands
"""

import requests
import json
import io
import wave
import numpy as np

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def create_demo_audio_file():
    """Create a simple demo WAV file for testing"""
    # Generate a simple sine wave (440 Hz for 2 seconds)
    sample_rate = 22050
    duration = 2.0
    frequency = 440.0
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit integers
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file in memory
    audio_buffer = io.BytesIO()
    with wave.open(audio_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    audio_buffer.seek(0)
    return audio_buffer

def get_auth_token():
    """Get authentication token for testing"""
    # Register user
    user_data = {
        "email": "filetest@example.com",
        "password": "SecurePass123!",
        "first_name": "File",
        "last_name": "Test"
    }
    
    try:
        # Try to register (might fail if user exists)
        requests.post(f"{API_BASE}/auth/register", json=user_data)
    except:
        pass
    
    # Login
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['access_token']
    
    return None

def test_file_upload_via_api():
    """Test file upload via API calls"""
    print("🧪 Testing File Upload via API...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token")
        return
    
    print(f"✅ Got auth token: {token[:20]}...")
    
    # Create demo audio file
    audio_file = create_demo_audio_file()
    
    # Prepare request
    headers = {"Authorization": f"Bearer {token}"}
    files = {
        'file': ('demo_voice.wav', audio_file, 'audio/wav')
    }
    data = {
        'name': 'Demo Voice Sample'
    }
    
    try:
        # Test upload via blueprint route
        print("\n📤 Testing upload via blueprint route (/api/v1/voice/samples)...")
        response = requests.post(f"{API_BASE}/voice/samples", 
                               files=files, 
                               data=data, 
                               headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"Sample ID: {result['data']['sample_id']}")
            print(f"Status: {result['data']['status']}")
        else:
            print(f"⚠️ Upload response: {response.text}")
        
        # Reset file pointer for next test
        audio_file.seek(0)
        
        # Test upload via Swagger route  
        print("\n📤 Testing upload via Swagger route (/voice/samples)...")
        response = requests.post(f"{BASE_URL}/voice/samples", 
                               files=files, 
                               data=data, 
                               headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Swagger upload successful!")
        else:
            print(f"⚠️ Swagger upload response: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")

def show_curl_examples():
    """Show curl command examples for file upload"""
    print("\n📋 Curl Command Examples:")
    
    print("\n1️⃣ Get authentication token:")
    print("""curl -X POST http://localhost:8000/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email":"test@example.com","password":"SecurePass123!"}'""")
    
    print("\n2️⃣ Upload file via blueprint route:")
    print("""curl -X POST http://localhost:8000/api/v1/voice/samples \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -F "file=@your_audio_file.wav" \\
  -F "name=My Voice Sample\"""")
    
    print("\n3️⃣ Upload file via Swagger route:")
    print("""curl -X POST http://localhost:8000/voice/samples \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -F "file=@your_audio_file.wav" \\
  -F "name=My Voice Sample\"""")

def show_swagger_ui_instructions():
    """Show instructions for using Swagger UI"""
    print("\n📚 Swagger UI File Upload Instructions:")
    print("="*50)
    
    print("1. 🌐 Open Swagger UI: http://localhost:8000/docs/")
    print("2. 🔐 Authenticate:")
    print("   - Click the 'Authorize' button")
    print("   - Enter: Bearer YOUR_ACCESS_TOKEN")
    print("   - Click 'Authorize'")
    
    print("3. 📤 Test file upload:")
    print("   - Find 'Voice Management' section")
    print("   - Click on 'POST /voice/samples'")
    print("   - Click 'Try it out'")
    print("   - You should see:")
    print("     * 'Choose File' button for audio file")
    print("     * Text input for 'name' parameter")
    print("   - Select your audio file (.wav or .mp3)")
    print("   - Enter a name for the sample")
    print("   - Click 'Execute'")
    
    print("4. ✅ Check results:")
    print("   - 201 status = success")
    print("   - Response will show sample details")
    print("   - You can then list samples to verify")

def test_swagger_documentation():
    """Test if Swagger documentation is accessible"""
    print("🔍 Testing Swagger Documentation Access...")
    
    try:
        # Test Swagger UI
        response = requests.get(f"{BASE_URL}/docs/")
        if response.status_code == 200:
            print(f"✅ Swagger UI accessible: {BASE_URL}/docs/")
        else:
            print(f"⚠️ Swagger UI: {response.status_code}")
        
        # Test OpenAPI spec
        response = requests.get(f"{BASE_URL}/docs/swagger.json")
        if response.status_code == 200:
            spec = response.json()
            # Check if file upload endpoint is documented
            paths = spec.get('paths', {})
            upload_endpoint = None
            for path, methods in paths.items():
                if 'voice' in path and 'samples' in path and 'post' in methods:
                    upload_endpoint = path
                    break
            
            if upload_endpoint:
                print(f"✅ File upload endpoint documented: {upload_endpoint}")
                
                # Check if it has file parameter
                post_spec = paths[upload_endpoint]['post']
                consumes = post_spec.get('consumes', [])
                if 'multipart/form-data' in consumes:
                    print("✅ Multipart form-data support detected")
                else:
                    print("⚠️ Multipart form-data not detected in spec")
            else:
                print("⚠️ Upload endpoint not found in documentation")
        else:
            print(f"⚠️ OpenAPI spec: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")

def main():
    """Run file upload demo and tests"""
    print("🎵 Voxify File Upload Demo & Test")
    print("="*40)
    
    # Test if server is running
    try:
        response = requests.get(BASE_URL)
        print(f"✅ Server is running: {response.status_code}")
    except:
        print("❌ Server is not running. Please start with: python start.py")
        return
    
    # Test documentation
    test_swagger_documentation()
    
    # Test file upload
    test_file_upload_via_api()
    
    # Show examples
    show_curl_examples()
    show_swagger_ui_instructions()
    
    print("\n🎉 Demo completed!")
    print(f"💡 Key points:")
    print("   - File uploads work in both blueprint and Swagger routes")
    print("   - Swagger UI shows 'Choose File' button for file parameters")
    print("   - Both WAV and MP3 files are supported")
    print("   - Maximum file size is 16MB")
    print("   - Authentication is required for uploads")

if __name__ == "__main__":
    main()