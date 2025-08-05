#!/usr/bin/env python3
"""
Quick test to verify file upload functionality in Swagger
"""

import requests
import json

def test_swagger_file_upload_spec():
    """Test that Swagger spec correctly shows file upload parameters"""
    print("🔍 Testing Swagger File Upload Specification...")
    
    try:
        # Get OpenAPI specification
        response = requests.get("http://localhost:8000/docs/swagger.json")
        if response.status_code != 200:
            print(f"❌ Could not get Swagger spec: {response.status_code}")
            return False
        
        spec = response.json()
        paths = spec.get('paths', {})
        
        # Look for voice samples upload endpoint
        upload_endpoints = []
        for path, methods in paths.items():
            if 'voice' in path and 'samples' in path and 'post' in methods:
                upload_endpoints.append((path, methods['post']))
        
        if not upload_endpoints:
            print("❌ No voice upload endpoints found")
            return False
        
        for path, endpoint_spec in upload_endpoints:
            print(f"\n📤 Checking endpoint: {path}")
            
            # Check content type
            consumes = endpoint_spec.get('consumes', [])
            if 'multipart/form-data' in consumes:
                print("✅ Supports multipart/form-data")
            else:
                print("⚠️ Missing multipart/form-data support")
            
            # Check parameters
            parameters = endpoint_spec.get('parameters', [])
            file_param = None
            name_param = None
            
            for param in parameters:
                if param.get('name') == 'file':
                    file_param = param
                elif param.get('name') == 'name':
                    name_param = param
            
            if file_param:
                param_type = file_param.get('type')
                param_in = file_param.get('in')
                print(f"✅ File parameter found: type={param_type}, in={param_in}")
                
                if param_type == 'file' and param_in == 'formData':
                    print("✅ Correct file parameter configuration")
                else:
                    print(f"⚠️ File parameter config: type={param_type}, in={param_in}")
            else:
                print("❌ File parameter not found")
            
            if name_param:
                print(f"✅ Name parameter found: type={name_param.get('type')}")
            else:
                print("❌ Name parameter not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Swagger spec: {e}")
        return False

def test_swagger_ui_accessibility():
    """Test that Swagger UI is accessible"""
    print("\n🌐 Testing Swagger UI Accessibility...")
    
    try:
        response = requests.get("http://localhost:8000/docs/")
        if response.status_code == 200:
            print("✅ Swagger UI is accessible")
            print("📋 URL: http://localhost:8000/docs/")
            
            # Check if it contains file upload related content
            content = response.text
            if 'multipart/form-data' in content:
                print("✅ Multipart form data support detected in UI")
            else:
                print("⚠️ Multipart form data not detected in UI content")
            
            return True
        else:
            print(f"❌ Swagger UI not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing Swagger UI: {e}")
        return False

def show_file_upload_instructions():
    """Show detailed instructions for file upload testing"""
    print("\n📚 File Upload Testing Instructions:")
    print("="*50)
    
    print("1. 🚀 Start the server:")
    print("   cd backend && python start.py")
    
    print("\n2. 🌐 Open Swagger UI:")
    print("   http://localhost:8000/docs/")
    
    print("\n3. 🔐 Authenticate:")
    print("   - First register/login to get a token")
    print("   - Click 'Authorize' button in Swagger UI")
    print("   - Enter: Bearer YOUR_ACCESS_TOKEN")
    
    print("\n4. 📤 Test file upload:")
    print("   - Find 'Voice Management' section")
    print("   - Locate 'POST /voice/samples' endpoint")
    print("   - Click 'Try it out'")
    print("   - You should see:")
    print("     * 'Choose File' button (for audio file)")
    print("     * Text input field (for sample name)")
    print("   - Select a WAV or MP3 file")
    print("   - Enter a sample name")
    print("   - Click 'Execute'")
    
    print("\n5. ✅ Verify results:")
    print("   - Check for 201 (Created) response")
    print("   - Response should contain sample details")
    print("   - Use 'GET /voice/samples' to list uploaded samples")
    
    print("\n💡 Troubleshooting:")
    print("   - If 'Choose File' button doesn't appear:")
    print("     * Check browser console for errors")
    print("     * Verify parameter type is 'file' in Swagger spec")
    print("     * Ensure 'multipart/form-data' is in consumes")
    print("   - If upload fails:")
    print("     * Check file format (only WAV/MP3 supported)")
    print("     * Verify file size < 16MB")
    print("     * Ensure valid authentication token")

def main():
    """Run file upload Swagger tests"""
    print("🎵 Swagger File Upload Verification")
    print("="*40)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Server is running: {response.status_code}")
    except:
        print("❌ Server is not running!")
        print("Please start the server with: cd backend && python start.py")
        return
    
    # Test Swagger specification
    spec_ok = test_swagger_file_upload_spec()
    
    # Test UI accessibility
    ui_ok = test_swagger_ui_accessibility()
    
    # Show instructions
    show_file_upload_instructions()
    
    # Summary
    print("\n" + "="*50)
    print("📋 Test Summary:")
    print(f"   Swagger Spec: {'✅' if spec_ok else '❌'}")
    print(f"   Swagger UI: {'✅' if ui_ok else '❌'}")
    
    if spec_ok and ui_ok:
        print("\n🎉 File upload should work correctly in Swagger UI!")
        print("📱 Go to http://localhost:8000/docs/ and test it out!")
    else:
        print("\n⚠️ Some issues detected. Check the output above.")

if __name__ == "__main__":
    main()