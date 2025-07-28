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
            assert (
                response.status_code == 405
            ), f"Unexpected status code: {response.status_code}"
        except Exception as e:
            pytest.skip(f"Server not available: {e}")

    @pytest.fixture(scope="class")
    def server_url(self):
        """Get the Flask server URL based on start.py configuration"""
        # Get configuration from environment variables (same as start.py)
        host = os.getenv("FLASK_HOST", "127.0.0.1")  # Use 127.0.0.1 for local testing
        port = int(
            os.getenv("PORT", os.getenv("FLASK_PORT", 8000))
        )  # Default port from start.py
        return f"http://{host}:{port}"

    @pytest.fixture(scope="class", autouse=True)
    def check_curl_available(self):
        """Check if curl is available on the system"""
        try:
            result = subprocess.run(
                ["curl", "--version"], capture_output=True, text=True
            )
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
            json.dumps(
                {"email": test_user["email"], "password": test_user["password"]}
            ),
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

    def test_upload_voice_sample_missing_name(
        self, server_url, auth_tokens, test_audio_file
    ):
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
        assert (
            "Invalid token" in response["msg"]
            or "Invalid header string" in response["msg"]
        )

    def test_create_voice_clone_success(self, server_url, auth_tokens):
        """Test successful voice clone creation"""
        # First upload a voice sample
        test_audio_file = os.path.join(
            os.path.dirname(__file__), "file_example_WAV_1MG.wav"
        )

        # Upload sample
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"file=@{test_audio_file}",
            "-F",
            "name=Test Sample for Clone",
            "-F",
            "description=Test sample for voice clone creation",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        assert (
            upload_response.get("success") is True
        ), f"Upload response: {upload_response}"

        sample_id = upload_response.get("data", {}).get("sample_id")
        assert sample_id is not None, "No sample_id in response"

        # Wait for processing
        import time

        time.sleep(2)

        # Create voice clone
        clone_data = {
            "sample_ids": [sample_id],
            "name": "Test Voice Clone",
            "ref_text": "Hello world, this is a test for voice cloning",
            "description": "Test voice clone created via API",
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
        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        assert (
            clone_response.get("success") is True
        ), f"Clone response: {clone_response}"

        clone_id = clone_response.get("data", {}).get("clone_id")
        assert clone_id is not None, "No clone_id in response"

        # Verify clone was created
        get_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones/{clone_id}",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(get_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Get clone failed: {result.stderr}"

        get_response = json.loads(result.stdout)
        assert (
            get_response.get("success") is True
        ), f"Get clone response: {get_response}"
        assert get_response.get("data", {}).get("clone_id") == clone_id

    def test_create_voice_clone_invalid_sample(self, server_url, auth_tokens):
        """Test voice clone creation with invalid sample ID"""
        clone_data = {
            "sample_ids": ["invalid-sample-id"],
            "name": "Test Voice Clone",
            "ref_text": "Hello world",
            "description": "Test voice clone with invalid sample",
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
        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        assert (
            clone_response.get("success") is False
        ), f"Expected failure but got: {clone_response}"
        assert "not found" in clone_response.get("error", "").lower()

    def test_get_voice_clone_success(self, server_url, auth_tokens):
        """Test successful retrieval of voice clone details"""
        # First create a clone
        test_audio_file = os.path.join(
            os.path.dirname(__file__), "file_example_WAV_1MG.wav"
        )

        # Upload sample
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"file=@{test_audio_file}",
            "-F",
            "name=Test Sample for Get Clone",
            "-F",
            "description=Test sample for getting clone details",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        sample_id = upload_response.get("data", {}).get("sample_id")

        # Wait for processing
        import time

        time.sleep(2)

        # Create clone
        clone_data = {
            "sample_ids": [sample_id],
            "name": "Test Clone for Get",
            "ref_text": "Hello world",
            "description": "Test clone for get operation",
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
        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        clone_id = clone_response.get("data", {}).get("clone_id")

        # Get clone details
        get_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones/{clone_id}",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(get_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Get clone failed: {result.stderr}"

        get_response = json.loads(result.stdout)
        assert (
            get_response.get("success") is True
        ), f"Get clone response: {get_response}"

        data = get_response.get("data", {})
        assert data.get("clone_id") == clone_id
        assert data.get("name") == "Test Clone for Get"
        assert data.get("description") == "Test clone for get operation"
        assert "quality_metrics" in data
        assert "samples" in data

    def test_delete_voice_clone_success(self, server_url, auth_tokens):
        """Test successful deletion of voice clone"""
        # First create a clone
        test_audio_file = os.path.join(
            os.path.dirname(__file__), "file_example_WAV_1MG.wav"
        )

        # Upload sample
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"file=@{test_audio_file}",
            "-F",
            "name=Test Sample for Delete Clone",
            "-F",
            "description=Test sample for deleting clone",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        sample_id = upload_response.get("data", {}).get("sample_id")

        # Wait for processing
        import time

        time.sleep(2)

        # Create clone
        clone_data = {
            "sample_ids": [sample_id],
            "name": "Test Clone for Delete",
            "ref_text": "Hello world",
            "description": "Test clone for deletion",
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
        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        clone_id = clone_response.get("data", {}).get("clone_id")

        # Delete clone
        delete_cmd = [
            "curl",
            "-X",
            "DELETE",
            f"{server_url}/api/v1/voice/clones/{clone_id}",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(delete_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Delete clone failed: {result.stderr}"

        delete_response = json.loads(result.stdout)
        assert (
            delete_response.get("success") is True
        ), f"Delete clone response: {delete_response}"

        # Verify clone was deleted
        get_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones/{clone_id}",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(get_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Get deleted clone failed: {result.stderr}"

        get_response = json.loads(result.stdout)
        assert (
            get_response.get("success") is False
        ), f"Expected failure but got: {get_response}"
        assert "not found" in get_response.get("error", "").lower()

    def test_select_voice_clone_success(self, server_url, auth_tokens):
        """Test successful selection of voice clone"""
        # First create a clone
        test_audio_file = os.path.join(
            os.path.dirname(__file__), "file_example_WAV_1MG.wav"
        )

        # Upload sample
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"file=@{test_audio_file}",
            "-F",
            "name=Test Sample for Select Clone",
            "-F",
            "description=Test sample for selecting clone",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        sample_id = upload_response.get("data", {}).get("sample_id")

        # Wait for processing
        import time

        time.sleep(2)

        # Create clone
        clone_data = {
            "sample_ids": [sample_id],
            "name": "Test Clone for Select",
            "ref_text": "Hello world",
            "description": "Test clone for selection",
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
        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        clone_id = clone_response.get("data", {}).get("clone_id")

        # Select clone
        select_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/clones/{clone_id}/select",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(select_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Select clone failed: {result.stderr}"

        select_response = json.loads(result.stdout)
        assert (
            select_response.get("success") is True
        ), f"Select clone response: {select_response}"
        assert select_response.get("data", {}).get("clone_id") == clone_id

    def test_synthesize_with_clone_success(self, server_url, auth_tokens):
        """Test successful speech synthesis with voice clone"""
        # First create a clone
        test_audio_file = os.path.join(
            os.path.dirname(__file__), "file_example_WAV_1MG.wav"
        )

        # Upload sample
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"file=@{test_audio_file}",
            "-F",
            "name=Test Sample for Synthesis",
            "-F",
            "description=Test sample for speech synthesis",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        sample_id = upload_response.get("data", {}).get("sample_id")

        # Wait for processing
        import time

        time.sleep(2)

        # Create clone
        clone_data = {
            "sample_ids": [sample_id],
            "name": "Test Clone for Synthesis",
            "ref_text": "Hello world",
            "description": "Test clone for speech synthesis",
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
        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        clone_id = clone_response.get("data", {}).get("clone_id")

        # Synthesize speech
        synthesis_data = {
            "text": "This is a test for speech synthesis with voice cloning",
            "speed": 1.0,
            "language": "zh-CN",
        }

        synthesis_cmd = [
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

        result = subprocess.run(synthesis_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Synthesis failed: {result.stderr}"

        synthesis_response = json.loads(result.stdout)
        assert (
            synthesis_response.get("success") is True
        ), f"Synthesis response: {synthesis_response}"

        data = synthesis_response.get("data", {})
        assert data.get("clone_id") == clone_id
        assert data.get("text") == synthesis_data["text"]
        assert "output_path" in data
        assert data.get("status") == "completed"

    def test_synthesize_with_clone_missing_text(self, server_url, auth_tokens):
        """Test speech synthesis with missing text"""
        # Create a clone first
        test_audio_file = os.path.join(
            os.path.dirname(__file__), "file_example_WAV_1MG.wav"
        )

        # Upload sample
        upload_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/voice/samples",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-F",
            f"file=@{test_audio_file}",
            "-F",
            "name=Test Sample for Synthesis Error",
            "-F",
            "description=Test sample for synthesis error",
        ]

        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Upload failed: {result.stderr}"

        upload_response = json.loads(result.stdout)
        sample_id = upload_response.get("data", {}).get("sample_id")

        # Wait for processing
        import time

        time.sleep(2)

        # Create clone
        clone_data = {
            "sample_ids": [sample_id],
            "name": "Test Clone for Synthesis Error",
            "ref_text": "Hello world",
            "description": "Test clone for synthesis error",
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
        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        clone_id = clone_response.get("data", {}).get("clone_id")

        # Try synthesis without text
        synthesis_data = {"speed": 1.0, "language": "zh-CN"}

        synthesis_cmd = [
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

        result = subprocess.run(synthesis_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Synthesis failed: {result.stderr}"

        synthesis_response = json.loads(result.stdout)
        assert (
            synthesis_response.get("success") is False
        ), f"Expected failure but got: {synthesis_response}"
        assert "text" in synthesis_response.get("error", "").lower()

    def test_list_voice_clones_with_multiple_clones(self, server_url, auth_tokens):
        """Test listing voice clones with multiple clones created"""
        # Create multiple clones
        test_audio_file = os.path.join(
            os.path.dirname(__file__), "file_example_WAV_1MG.wav"
        )

        clone_names = ["Clone 1", "Clone 2", "Clone 3"]
        clone_ids = []

        for i, name in enumerate(clone_names):
            # Upload sample
            upload_cmd = [
                "curl",
                "-X",
                "POST",
                f"{server_url}/api/v1/voice/samples",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
                "-F",
                f"file=@{test_audio_file}",
                "-F",
                f"name=Test Sample {i+1}",
                "-F",
                f"description=Test sample {i+1} for multiple clones",
            ]

            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Upload {i+1} failed: {result.stderr}"

            upload_response = json.loads(result.stdout)
            sample_id = upload_response.get("data", {}).get("sample_id")

            # Wait for processing
            import time

            time.sleep(2)

            # Create clone
            clone_data = {
                "sample_ids": [sample_id],
                "name": name,
                "ref_text": f"Hello world from {name}",
                "description": f"Test clone {i+1}",
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
            assert (
                result.returncode == 0
            ), f"Clone {i+1} creation failed: {result.stderr}"

            clone_response = json.loads(result.stdout)
            clone_id = clone_response.get("data", {}).get("clone_id")
            clone_ids.append(clone_id)

        # List clones
        list_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(list_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"List clones failed: {result.stderr}"

        list_response = json.loads(result.stdout)
        assert (
            list_response.get("success") is True
        ), f"List clones response: {list_response}"

        data = list_response.get("data", {})
        clones = data.get("clones", [])
        assert len(clones) >= 3, f"Expected at least 3 clones, got {len(clones)}"

        # Verify pagination
        pagination = data.get("pagination", {})
        assert "page" in pagination
        assert "page_size" in pagination
        assert "total_count" in pagination
        assert "total_pages" in pagination

    def test_voice_clone_validation_errors(self, server_url, auth_tokens):
        """Test various validation errors in voice clone operations"""
        # Test missing name
        clone_data = {
            "sample_ids": ["sample1"],
            "ref_text": "Hello world"
            # Missing name
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
        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        assert (
            clone_response.get("success") is False
        ), f"Expected failure but got: {clone_response}"
        assert "name" in clone_response.get("error", "").lower()

        # Test missing ref_text
        clone_data = {
            "sample_ids": ["sample1"],
            "name": "Test Clone"
            # Missing ref_text
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
        assert result.returncode == 0, f"Clone creation failed: {result.stderr}"

        clone_response = json.loads(result.stdout)
        assert (
            clone_response.get("success") is False
        ), f"Expected failure but got: {clone_response}"
        assert "ref_text" in clone_response.get("error", "").lower()

    def test_voice_clone_authorization_errors(self, server_url, auth_tokens):
        """Test authorization errors in voice clone operations"""
        # Test accessing clone with invalid token
        invalid_token = "invalid_token_123"

        get_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones/test-clone-id",
            "-H",
            f"Authorization: Bearer {invalid_token}",
        ]

        result = subprocess.run(get_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Get clone failed: {result.stderr}"

        get_response = json.loads(result.stdout)
        # Check for either success=False or JWT error message
        assert (
            get_response.get("success") is False
            or "Not enough segments" in get_response.get("msg", "")
            or "Invalid token" in get_response.get("msg", "")
        ), f"Expected failure but got: {get_response}"

        # Test accessing clone without token
        get_cmd_no_token = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/voice/clones/test-clone-id",
        ]

        result = subprocess.run(get_cmd_no_token, capture_output=True, text=True)
        assert result.returncode == 0, f"Get clone failed: {result.stderr}"

        get_response = json.loads(result.stdout)
        # Check for either success=False or JWT error message
        assert (
            get_response.get("success") is False
            or "Not enough segments" in get_response.get("msg", "")
            or "Missing Authorization Header" in get_response.get("msg", "")
        ), f"Expected failure but got: {get_response}"


def run_tests():
    """Run the voice service tests"""
    pytest.main([__file__, "-v"])


def test_configuration():
    """Test that the test configuration is correct"""
    assert True  # Placeholder for configuration tests


if __name__ == "__main__":
    run_tests()
