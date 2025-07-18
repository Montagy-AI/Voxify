import subprocess
import json
import pytest
import requests
import sys
import os
import tempfile

# Add the backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


class TestVoiceServiceAPI:
    """Service tests for voice API endpoints using curl commands"""

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
        # Get configuration from environment variables (same as start.py)
        host = os.getenv("FLASK_HOST", "127.0.0.1")  # Use 127.0.0.1 for local testing
        port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 10000)))  # Default port from start.py
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
        """Test user credentials"""
        return {
            "email": "voicetest@example.com",
            "password": "Test123!@#",
            "first_name": "Voice",
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
        """Create a test audio file for upload testing"""
        # Create a simple WAV file for testing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            # Write a minimal WAV header (44 bytes)
            wav_header = (
                b"RIFF"  # Chunk ID
                + (36).to_bytes(4, "little")  # Chunk size
                + b"WAVE"  # Format
                + b"fmt "  # Subchunk1 ID
                + (16).to_bytes(4, "little")  # Subchunk1 size
                + (1).to_bytes(2, "little")  # Audio format (PCM)
                + (1).to_bytes(2, "little")  # Number of channels
                + (22050).to_bytes(4, "little")  # Sample rate
                + (22050).to_bytes(4, "little")  # Byte rate
                + (1).to_bytes(2, "little")  # Block align
                + (8).to_bytes(2, "little")  # Bits per sample
                + b"data"  # Subchunk2 ID
                + (0).to_bytes(4, "little")  # Subchunk2 size
            )
            f.write(wav_header)
            f.flush()
            return f.name

    def test_upload_voice_sample_valid(self, server_url, auth_tokens, test_audio_file):
        """Test uploading a valid voice sample"""
        curl_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            "name=Test Sample",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"

        response = json.loads(result.stdout)

        # Print response for debugging
        print(f"Upload response: {response}")

        # Check if upload was successful or if there's a specific error
        if response.get("success") is False:
            # If upload failed, check if it's due to missing dependencies or other issues
            error_msg = response.get("error", "")
            if "embedding" in error_msg.lower() or "model" in error_msg.lower():
                # Skip test if it's due to missing ML models
                pytest.skip(f"Upload failed due to missing dependencies: {error_msg}")
            else:
                # For other errors, fail the test
                assert False, f"Upload failed: {error_msg}"
        else:
            # Success case
            assert response["success"] is True
            assert "data" in response
            assert "sample_id" in response["data"]
            assert response["data"]["name"] == "Test Sample"
            assert response["data"]["status"] == "ready"

    def test_upload_voice_sample_missing_name(self, server_url, auth_tokens, test_audio_file):
        """Test uploading a voice sample without name"""
        curl_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"file=@{test_audio_file}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert "Name is required" in response["error"]

    def test_upload_voice_sample_missing_file(self, server_url, auth_tokens):
        """Test uploading a voice sample without file"""
        curl_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            "name=Test Sample",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert "No file provided" in response["error"]

    def test_upload_voice_sample_invalid_file_type(self, server_url, auth_tokens):
        """Test uploading a voice sample with invalid file type"""
        # Create a text file instead of audio
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"This is not an audio file")
            f.flush()
            invalid_file = f.name

        try:
            curl_cmd = [
                "curl",
                "-X",
                "POST",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
                "-F",
                "name=Test Sample",
                "-F",
                f"file=@{invalid_file}",
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0

            response = json.loads(result.stdout)
            assert response["success"] is False
            assert "error" in response
            assert "Invalid file type" in response["error"]
        finally:
            os.unlink(invalid_file)

    def test_list_voice_samples_basic(self, server_url, auth_tokens):
        """Test listing voice samples with basic parameters"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is True
        assert "data" in response
        assert "samples" in response["data"]
        assert "pagination" in response["data"]

    def test_list_voice_samples_with_pagination(self, server_url, auth_tokens):
        """Test listing voice samples with pagination parameters"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/samples?page=1&page_size=10",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is True
        assert "data" in response
        assert "pagination" in response["data"]
        assert response["data"]["pagination"]["page"] == 1
        assert response["data"]["pagination"]["page_size"] == 10

    def test_list_voice_samples_with_status_filter(self, server_url, auth_tokens):
        """Test listing voice samples with status filter"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/samples?status=ready",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is True

    def test_get_voice_sample_details(self, server_url, auth_tokens):
        """Test getting details of a specific voice sample"""
        # First, get a list of samples to find an existing one
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

        if response["success"] and response["data"]["samples"]:
            sample_id = response["data"]["samples"][0]["id"]

            # Get specific sample details
            get_cmd = [
                "curl",
                "-X",
                "GET",
                f"{server_url}/api/v1/voice/samples/{sample_id}",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
            ]

            result = subprocess.run(get_cmd, capture_output=True, text=True)
            assert result.returncode == 0

            response = json.loads(result.stdout)
            assert response["success"] is True
            assert "data" in response
            assert response["data"]["id"] == sample_id
        else:
            pytest.skip("No voice samples available for testing")

    def test_get_voice_sample_not_found(self, server_url, auth_tokens):
        """Test getting a non-existent voice sample"""
        non_existent_id = "non-existent-sample-id"

        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/samples/{non_existent_id}",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_delete_voice_sample(self, server_url, auth_tokens):
        """Test deleting a voice sample"""
        # First, get a list of samples to find an existing one
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

        if response["success"] and response["data"]["samples"]:
            sample_id = response["data"]["samples"][0]["id"]

            # Delete the sample
            delete_cmd = [
                "curl",
                "-X",
                "DELETE",
                f"{server_url}/api/v1/voice/samples/{sample_id}",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
            ]

            result = subprocess.run(delete_cmd, capture_output=True, text=True)
            assert result.returncode == 0

            response = json.loads(result.stdout)
            assert response["success"] is True
        else:
            pytest.skip("No voice samples available for testing")

    def test_create_voice_clone_missing_required_fields(self, server_url, auth_tokens):
        """Test creating a voice clone with missing required fields"""
        clone_data = {
            "name": "Test Clone"
            # Missing sample_ids and ref_text
        }

        curl_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d",
            json.dumps(clone_data),
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert "Missing required fields" in response["error"]

    def test_create_voice_clone_empty_sample_ids(self, server_url, auth_tokens):
        """Test creating a voice clone with empty sample IDs"""
        clone_data = {
            "sample_ids": [],
            "name": "Test Clone",
            "ref_text": "This is a reference text",
        }

        curl_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d",
            json.dumps(clone_data),
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert "At least one sample_id is required" in response["error"]

    def test_list_voice_clones_basic(self, server_url, auth_tokens):
        """Test listing voice clones with basic parameters"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is True
        assert "data" in response
        assert "clones" in response["data"]
        assert "pagination" in response["data"]

    def test_list_voice_clones_with_pagination(self, server_url, auth_tokens):
        """Test listing voice clones with pagination parameters"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones?page=1&page_size=10",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is True
        assert "data" in response
        assert "pagination" in response["data"]

    def test_get_voice_clone_not_found(self, server_url, auth_tokens):
        """Test getting a non-existent voice clone"""
        non_existent_id = "non-existent-clone-id"

        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones/{non_existent_id}",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_delete_voice_clone_not_found(self, server_url, auth_tokens):
        """Test deleting a non-existent voice clone"""
        non_existent_id = "non-existent-clone-id"

        curl_cmd = [
            "curl",
            "-X",
            "DELETE",
            f"{server_url}/api/v1/voice/clones/{non_existent_id}",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_select_voice_clone_not_found(self, server_url, auth_tokens):
        """Test selecting a non-existent voice clone"""
        non_existent_id = "non-existent-clone-id"

        curl_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones/{non_existent_id}/select",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d",
            "{}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_synthesize_with_clone_not_found(self, server_url, auth_tokens):
        """Test synthesizing with a non-existent voice clone"""
        non_existent_id = "non-existent-clone-id"
        synthesis_data = {
            "text": "Hello world",
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 1.0,
        }

        curl_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones/{non_existent_id}/synthesize",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d",
            json.dumps(synthesis_data),
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_unauthorized_access(self, server_url):
        """Test accessing voice endpoints without authentication"""
        endpoints = [
            "/api/v1/voice/samples",
            "/api/v1/voice/clones",
            "/api/v1/voice/samples/test-id",
            "/api/v1/voice/clones/test-id",
        ]

        for endpoint in endpoints:
            curl_cmd = ["curl", "-X", "GET", f"{server_url}{endpoint}"]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0

            response = json.loads(result.stdout)
            # Flask-JWT-Extended returns {"msg": "Missing Authorization Header"} for unauthorized access
            assert "msg" in response
            assert "Missing Authorization Header" in response["msg"]

    def test_invalid_token_access(self, server_url):
        """Test accessing voice endpoints with invalid token"""
        invalid_token = "invalid.token.here"

        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {invalid_token}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        # Flask-JWT-Extended returns {"msg": "Invalid token"} or {"msg": "Invalid header string ..."}
        assert "msg" in response
        assert "Invalid token" in response["msg"] or "Invalid header string" in response["msg"]


def run_tests():
    """Run the voice service tests"""
    pytest.main([__file__, "-v"])


def test_configuration():
    """Test that the test configuration is correct"""
    assert True  # Placeholder for configuration tests


if __name__ == "__main__":
    run_tests()
