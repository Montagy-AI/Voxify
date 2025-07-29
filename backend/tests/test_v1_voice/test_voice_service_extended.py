"""
Extended Voice Service Tests
Additional service-level tests for voice API endpoints
"""

import subprocess
import json
import pytest
import requests
import sys
import os
import tempfile
import time

# Add the backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


class TestVoiceServiceExtended:
    """Extended service tests for voice API endpoints"""

    @pytest.fixture(scope="class", autouse=True)
    def check_server(self, server_url):
        """Check if server is running before tests"""
        try:
            response = requests.get(f"{server_url}/api/v1/auth/login", timeout=5)
            assert response.status_code == 405, f"Unexpected status code: {response.status_code}"
        except Exception as e:
            pytest.skip(f"Server not available: {e}")

    @pytest.fixture(scope="class")
    def server_url(self):
        """Get the Flask server URL based on start.py configuration"""
        host = os.getenv("FLASK_HOST", "127.0.0.1")
        port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 8000)))
        return f"http://{host}:{port}"

    @pytest.fixture(scope="class", autouse=True)
    def check_curl_available(self):
        """Check if curl is available on the system"""
        try:
            result = subprocess.run(["curl", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                pytest.skip("curl is not available on this system")
        except FileNotFoundError:
            pytest.skip("curl is not installed on this system")

    @pytest.fixture(scope="class")
    def test_user(self):
        """Test user credentials for extended tests"""
        return {
            "email": "extended_test@example.com",
            "password": "ExtendedTest123!@#",
            "first_name": "Extended",
            "last_name": "Tester",
        }

    @pytest.fixture(scope="class")
    def auth_tokens(self, server_url, test_user):
        """Get authentication tokens for testing"""
        # Register user
        register_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/auth/register",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(test_user),
        ]
        subprocess.run(register_cmd, capture_output=True)

        # Login to get tokens
        login_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/auth/login",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps({"email": test_user["email"], "password": test_user["password"]}),
        ]
        result = subprocess.run(login_cmd, capture_output=True, text=True)
        response = json.loads(result.stdout)
        return {
            "access_token": response.get("data", {}).get("access_token"),
            "refresh_token": response.get("data", {}).get("refresh_token"),
        }

    @pytest.fixture(scope="class")
    def test_audio_file(self):
        """Use the local file_example_WAV_1MG.wav as the test audio file."""
        return os.path.join(os.path.dirname(__file__), "file_example_WAV_1MG.wav")

    def test_voice_service_info(self, server_url, auth_tokens):
        """Test voice service info endpoint"""
        info_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/info",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(info_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Service info failed: {result.stderr}"

        info_response = json.loads(result.stdout)
        assert info_response.get("success") is True, f"Service info failed: {info_response}"

        data = info_response["data"]
        assert "service" in data
        assert "version" in data
        assert "features" in data
        assert "supported_formats" in data

    def test_voice_models_endpoint(self, server_url, auth_tokens):
        """Test voice models endpoint"""
        models_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/models",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(models_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Models endpoint failed: {result.stderr}"

        models_response = json.loads(result.stdout)
        assert models_response.get("success") is True, f"Models endpoint failed: {models_response}"

        data = models_response["data"]
        assert "models" in data
        assert len(data["models"]) > 0

    def test_upload_voice_sample_large_file(self, server_url, auth_tokens, test_audio_file):
        """Test uploading a large voice sample"""
        # For testing, we'll use the existing file but test the concept
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            "name=Large Test Sample",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Large file upload failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        assert upload_response.get("success") is True, f"Large file upload failed: {upload_response}"

    def test_upload_voice_sample_with_description(self, server_url, auth_tokens, test_audio_file):
        """Test uploading voice sample with description"""
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            "name=Sample with Description",
            "-F",
            "description=This is a test sample with description",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload with description failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        assert upload_response.get("success") is True, f"Upload with description failed: {upload_response}"

    def test_list_voice_samples_with_filters(self, server_url, auth_tokens):
        """Test listing voice samples with various filters"""
        # Test with status filter
        list_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/samples?status=ready",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(list_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"List with status filter failed: {result.stderr}"

        list_response = json.loads(result.stdout)
        assert list_response.get("success") is True, f"List with status filter failed: {list_response}"

        # Test with pagination
        list_cmd_paginated = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/samples?page=1&page_size=5",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(list_cmd_paginated, capture_output=True, text=True)
        assert result.returncode == 0, f"List with pagination failed: {result.stderr}"

        list_response = json.loads(result.stdout)
        assert list_response.get("success") is True, f"List with pagination failed: {list_response}"

    def test_create_voice_clone_with_advanced_config(self, server_url, auth_tokens, test_audio_file):
        """Test creating voice clone with advanced configuration"""
        # First upload a sample
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            "name=Advanced Clone Sample",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload for advanced clone failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        assert upload_response.get("success") is True, f"Upload for advanced clone failed: {upload_response}"

        sample_id = upload_response["data"]["sample_id"]

        # Create clone with advanced configuration
        clone_data = {
            "sample_ids": [sample_id],
            "name": "Advanced Test Clone",
            "ref_text": "This is an advanced test reference text for voice cloning with extended configuration",
            "description": "Advanced voice clone with extended configuration for testing",
            "language": "zh-CN",
        }

        clone_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(clone_data),
        ]

        result = subprocess.run(clone_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Advanced clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        assert clone_response.get("success") is True, f"Advanced clone creation failed: {clone_response}"

    def test_synthesize_with_advanced_parameters(self, server_url, auth_tokens, test_audio_file):
        """Test speech synthesis with advanced parameters"""
        # First create a clone
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            "name=Synthesis Test Sample",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload for synthesis test failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        assert upload_response.get("success") is True, f"Upload for synthesis test failed: {upload_response}"

        sample_id = upload_response["data"]["sample_id"]

        # Create clone
        clone_data = {
            "sample_ids": [sample_id],
            "name": "Synthesis Test Clone",
            "ref_text": "This is a test reference text for synthesis testing",
        }

        clone_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(clone_data),
        ]

        result = subprocess.run(clone_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Clone creation for synthesis failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        assert clone_response.get("success") is True, f"Clone creation for synthesis failed: {clone_response}"

        clone_id = clone_response["data"]["clone_id"]

        # Test synthesis with advanced parameters
        synthesis_data = {
            "text": "这是一个高级语音合成测试。Hello, this is an advanced speech synthesis test with multiple parameters.",
            "speed": 1.2,
            "language": "zh-CN",
            "pitch": 1.0,
            "volume": 0.8,
        }

        synthesize_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones/{clone_id}/synthesize",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(synthesis_data),
        ]

        result = subprocess.run(synthesize_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Advanced synthesis failed: {result.stderr}"

        synthesis_response = json.loads(result.stdout)
        assert synthesis_response.get("success") is True, f"Advanced synthesis failed: {synthesis_response}"

    def test_concurrent_voice_operations(self, server_url, auth_tokens, test_audio_file):
        """Test concurrent voice operations"""
        import threading
        import time

        results = []

        def upload_sample(thread_id):
            """Upload a sample in a separate thread"""
            upload_cmd = [
                "curl",
                "-X",
                "POST",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
                "-F",
                f"name=Concurrent Sample {thread_id}",
                "-F",
                f"file=@{test_audio_file}",
            ]

            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            response = json.loads(result.stdout)
            results.append((thread_id, response.get("success")))

        # Start multiple upload threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=upload_sample, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) == 3
        for thread_id, success in results:
            assert success is True, f"Thread {thread_id} upload failed"

    def test_voice_sample_metadata_retrieval(self, server_url, auth_tokens, test_audio_file):
        """Test retrieving detailed voice sample metadata"""
        # First upload a sample
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            "name=Metadata Test Sample",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload for metadata test failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        assert upload_response.get("success") is True, f"Upload for metadata test failed: {upload_response}"

        sample_id = upload_response["data"]["sample_id"]

        # Get detailed sample information
        get_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/samples/{sample_id}",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(get_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Get sample metadata failed: {result.stderr}"

        get_response = json.loads(result.stdout)
        assert get_response.get("success") is True, f"Get sample metadata failed: {get_response}"

        data = get_response["data"]
        assert "id" in data
        assert "name" in data
        assert "file_path" in data
        assert "duration" in data
        assert "format" in data

    def test_voice_clone_selection_workflow(self, server_url, auth_tokens, test_audio_file):
        """Test complete voice clone selection workflow"""
        # Upload multiple samples
        sample_ids = []
        for i in range(2):
            upload_cmd = [
                "curl",
                "-X",
                "POST",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
                "-F",
                f"name=Selection Test Sample {i+1}",
                "-F",
                f"file=@{test_audio_file}",
            ]

            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Upload {i+1} for selection test failed: {result.stderr}"

            upload_response = json.loads(result.stdout)
            assert upload_response.get("success") is True, f"Upload {i+1} for selection test failed: {upload_response}"

            sample_ids.append(upload_response["data"]["sample_id"])

        # Create multiple clones
        clone_ids = []
        for i in range(2):
            clone_data = {
                "sample_ids": [sample_ids[i]],
                "name": f"Selection Test Clone {i+1}",
                "ref_text": f"This is reference text for clone {i+1}",
            }

            clone_cmd = [
                "curl",
                "-X",
                "POST",
                f"{server_url}/api/v1/voice/clones",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps(clone_data),
            ]

            result = subprocess.run(clone_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Clone {i+1} creation failed: {result.stderr}"

            clone_response = json.loads(result.stdout)
            assert clone_response.get("success") is True, f"Clone {i+1} creation failed: {clone_response}"

            clone_ids.append(clone_response["data"]["clone_id"])

        # Select the first clone
        select_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones/{clone_ids[0]}/select",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(select_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Clone selection failed: {result.stderr}"

        select_response = json.loads(result.stdout)
        assert select_response.get("success") is True, f"Clone selection failed: {select_response}"

        # Verify selection by listing clones
        list_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(list_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"List clones after selection failed: {result.stderr}"

        list_response = json.loads(result.stdout)
        assert list_response.get("success") is True, f"List clones after selection failed: {list_response}"

    def test_voice_service_rate_limiting(self, server_url, auth_tokens, test_audio_file):
        """Test voice service rate limiting behavior"""
        # Perform multiple rapid requests
        responses = []

        for i in range(5):
            # List samples (lightweight operation)
            list_cmd = [
                "curl",
                "-X",
                "GET",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
            ]

            result = subprocess.run(list_cmd, capture_output=True, text=True)
            response = json.loads(result.stdout)
            responses.append(response.get("success"))

            # Small delay between requests
            time.sleep(0.1)

        # All requests should succeed (no rate limiting on lightweight operations)
        assert all(responses), "Rate limiting test failed - some requests were blocked"

    def test_voice_service_error_responses(self, server_url, auth_tokens):
        """Test voice service error response formats"""
        # Test with invalid sample ID
        get_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/samples/invalid-sample-id",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(get_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Get invalid sample failed: {result.stderr}"

        get_response = json.loads(result.stdout)
        assert get_response.get("success") is False, f"Expected error but got success: {get_response}"
        assert "error" in get_response, f"No error message in response: {get_response}"

        # Test with invalid clone ID
        get_clone_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones/invalid-clone-id",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(get_clone_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Get invalid clone failed: {result.stderr}"

        get_clone_response = json.loads(result.stdout)
        assert get_clone_response.get("success") is False, f"Expected error but got success: {get_clone_response}"
        assert "error" in get_clone_response, f"No error message in response: {get_clone_response}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
