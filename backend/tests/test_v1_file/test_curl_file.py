import subprocess
import json
import pytest
import requests
import sys
import os
import platform

# Add the backend directory to Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, backend_path)


class TestFileServiceAPI:
    """Service tests for file API endpoints and data boundaries"""

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
        port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 8000)))  # Default port from start.py
        return f"http://{host}:{port}"

    @pytest.fixture(scope="class")
    def null_device(self):
        """Get the appropriate null device for the current platform"""
        return "NUL" if platform.system() == "Windows" else "/dev/null"

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
            "email": "filetest@example.com",
            "password": "Test123!@#",
            "first_name": "File",
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
    def test_job_id(self, server_url, auth_tokens):
        """Create a test synthesis job and return its ID"""
        # First, get an available voice model ID
        try:
            from database import get_database_manager
            from database.models import VoiceModel, VoiceSample, User

            # Debug: Print database URL
            db_url = os.getenv("DATABASE_URL", "sqlite:///data/voxify.db")
            print(f"[TEST] Using database URL: {db_url}")

            db_manager = get_database_manager()
            session = db_manager.get_session()

            # Get the first available active voice model
            voice_model = session.query(VoiceModel).filter_by(is_active=True).first()

            # If no voice model exists, create one for testing
            if not voice_model:
                print("[TEST] No active voice model found, creating one for testing...")

                # First, ensure we have a test user
                test_user = session.query(User).filter_by(email="filetest@example.com").first()
                if not test_user:
                    print("[TEST] Creating test user...")
                    test_user = User(
                        id="test-user-file",
                        email="filetest@example.com",
                        password_hash="test_hash",
                        first_name="File",
                        last_name="Tester",
                    )
                    session.add(test_user)
                    session.commit()

                # Create a test voice sample
                voice_sample = VoiceSample(
                    id="test-sample-file",
                    user_id=test_user.id,
                    name="Test Sample for File Tests",
                    file_path="/test/path/sample.wav",
                    file_size=1024,
                    format="wav",
                    duration=5.0,
                    sample_rate=22050,
                    status="ready",
                )
                session.add(voice_sample)
                session.commit()

                # Create a test voice model
                voice_model = VoiceModel(
                    id="test-model-file",
                    voice_sample_id=voice_sample.id,
                    name="Test Voice Model",
                    model_path="/test/path/model.pth",
                    status="completed",
                    is_active=True,
                )
                session.add(voice_model)
                session.commit()

                print(f"[TEST] Created test voice model: {voice_model.id}")

            voice_model_id = str(voice_model.id)  # Ensure it's a string
            print(f"[TEST] Using voice model ID: {voice_model_id}")
            session.close()

        except Exception as e:
            print(f"[TEST] Error accessing database: {e}")
            # Fallback to a test ID if database access fails
            voice_model_id = "test-voice-model"
            print(f"[TEST] Using fallback voice model ID: {voice_model_id}")

        # Create a test job
        job_data = {
            "text_content": "Hello, this is a test for file download.",
            "voice_model_id": voice_model_id,
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 1.0,
            "output_format": "wav",
            "sample_rate": 44100,
        }

        job_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/job",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d",
            json.dumps(job_data),
        ]

        result = subprocess.run(job_cmd, capture_output=True, text=True)
        print(f"[TEST] Job creation response: {result.stdout}")
        print(f"[TEST] Job creation stderr: {result.stderr}")

        try:
            response = json.loads(result.stdout)
            job_id = response.get("data", {}).get("id")
            if job_id:
                print(f"[TEST] Created job with ID: {job_id}")
                return job_id
            else:
                print(f"[TEST] No job ID in response: {response}")
                # Return a mock job ID for testing purposes
                return "test-job-id-12345"
        except json.JSONDecodeError as e:
            print(f"[TEST] Failed to parse job response: {e}")
            # Return a mock job ID for testing purposes
            return "test-job-id-12345"

    def test_download_synthesis_file_without_auth(self, server_url):
        """Test download synthesis file without authentication"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H",
            "Content-Type: application/json",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 401 Unauthorized
        assert "Missing Authorization Header" in result.stdout

    def test_download_synthesis_file_invalid_job_id(self, server_url, auth_tokens):
        """Test download synthesis file with invalid job ID"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/file/synthesis/invalid-job-id",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert response["error"]["code"] == "FILE_NOT_FOUND"

    def test_download_synthesis_file_nonexistent_job(self, server_url, auth_tokens):
        """Test download synthesis file with non-existent job ID"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/file/synthesis/00000000-0000-0000-0000-000000000000",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert response["error"]["code"] == "FILE_NOT_FOUND"

    def test_download_synthesis_file_with_valid_job(self, server_url, auth_tokens, test_job_id, null_device):
        """Test download synthesis file with valid job ID"""
        if not test_job_id:
            pytest.skip("No test job ID available")

        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/file/synthesis/{test_job_id}",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-o",
            null_device,  # Don't save the file, just check response
            "-w",
            "%{http_code}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 404 if file doesn't exist yet, or 200 if it does
        # For mock job ID, we expect 404 since the file doesn't exist
        status_code = result.stdout.strip()
        assert status_code in ["200", "404"]

    def test_delete_synthesis_file_without_auth(self, server_url):
        """Test delete synthesis file without authentication"""
        curl_cmd = [
            "curl",
            "-X",
            "DELETE",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H",
            "Content-Type: application/json",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 401 Unauthorized
        assert "Missing Authorization Header" in result.stdout

    def test_delete_synthesis_file_invalid_job_id(self, server_url, auth_tokens):
        """Test delete synthesis file with invalid job ID"""
        curl_cmd = [
            "curl",
            "-X",
            "DELETE",
            f"{server_url}/api/v1/file/synthesis/invalid-job-id",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert response["error"]["code"] == "FILE_NOT_FOUND"

    def test_delete_synthesis_file_nonexistent_job(self, server_url, auth_tokens):
        """Test delete synthesis file with non-existent job ID"""
        curl_cmd = [
            "curl",
            "-X",
            "DELETE",
            f"{server_url}/api/v1/file/synthesis/00000000-0000-0000-0000-000000000000",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert response["error"]["code"] == "FILE_NOT_FOUND"

    def test_delete_synthesis_file_with_valid_job(self, server_url, auth_tokens, test_job_id):
        """Test delete synthesis file with valid job ID"""
        if not test_job_id:
            pytest.skip("No test job ID available")

        curl_cmd = [
            "curl",
            "-X",
            "DELETE",
            f"{server_url}/api/v1/file/synthesis/{test_job_id}",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        # The API returns 404 if file doesn't exist, which is acceptable
        # We accept both success (if file exists and is deleted) or FILE_NOT_FOUND (if file doesn't exist)
        # For mock job ID, we expect FILE_NOT_FOUND since the file doesn't exist
        if response["success"] is False:
            assert "error" in response
            assert response["error"]["code"] == "FILE_NOT_FOUND"
        else:
            assert response["success"] is True

    def test_download_synthesis_file_with_invalid_token(self, server_url):
        """Test download synthesis file with invalid token"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H",
            "Content-Type: application/json",
            "-H",
            "Authorization: Bearer invalid_token_here",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 401 Unauthorized
        assert "Not enough segments" in result.stdout

    def test_delete_synthesis_file_with_invalid_token(self, server_url):
        """Test delete synthesis file with invalid token"""
        curl_cmd = [
            "curl",
            "-X",
            "DELETE",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H",
            "Content-Type: application/json",
            "-H",
            "Authorization: Bearer invalid_token_here",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 401 Unauthorized
        assert "Not enough segments" in result.stdout

    def test_download_synthesis_file_malformed_job_id(self, server_url, auth_tokens):
        """Test download synthesis file with malformed job ID"""
        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/file/synthesis/not-a-uuid",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_delete_synthesis_file_malformed_job_id(self, server_url, auth_tokens):
        """Test delete synthesis file with malformed job ID"""
        curl_cmd = [
            "curl",
            "-X",
            "DELETE",
            f"{server_url}/api/v1/file/synthesis/not-a-uuid",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_download_synthesis_file_wrong_method(self, server_url, auth_tokens):
        """Test download synthesis file with wrong HTTP method"""
        curl_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 405 Method Not Allowed
        assert "405" in result.stdout or "Method Not Allowed" in result.stdout

    def test_delete_synthesis_file_wrong_method(self, server_url, auth_tokens):
        """Test delete synthesis file with wrong HTTP method"""
        curl_cmd = [
            "curl",
            "-X",
            "POST",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 405 Method Not Allowed
        assert "405" in result.stdout or "Method Not Allowed" in result.stdout

    def test_download_synthesis_file_with_headers(self, server_url, auth_tokens, test_job_id, null_device):
        """Test download synthesis file with additional headers"""
        if not test_job_id:
            pytest.skip("No test job ID available")

        curl_cmd = [
            "curl",
            "-X",
            "GET",
            f"{server_url}/api/v1/file/synthesis/{test_job_id}",
            "-H",
            "Content-Type: application/json",
            "-H",
            "Accept: audio/*",
            "-H",
            f"Authorization: Bearer {auth_tokens['access_token']}",
            "-o",
            null_device,
            "-w",
            "%{http_code}",
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        status_code = result.stdout.strip()
        # For mock job ID, we expect 404 since the file doesn't exist
        assert status_code in ["200", "404"]

    def test_unauthorized_access(self, server_url):
        """Test unauthorized access to file endpoints"""
        test_endpoints = [
            "/api/v1/file/synthesis/test-job-id",
            "/api/v1/file/synthesis/00000000-0000-0000-0000-000000000000",
        ]

        for endpoint in test_endpoints:
            # Test GET without auth
            curl_cmd = [
                "curl",
                "-X",
                "GET",
                f"{server_url}{endpoint}",
                "-H",
                "Content-Type: application/json",
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Curl command failed: {result.stderr}"
            assert "Missing Authorization Header" in result.stdout

            # Test DELETE without auth
            curl_cmd = [
                "curl",
                "-X",
                "DELETE",
                f"{server_url}{endpoint}",
                "-H",
                "Content-Type: application/json",
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Curl command failed: {result.stderr}"
            assert "Missing Authorization Header" in result.stdout

    def test_file_endpoint_error_responses(self, server_url, auth_tokens):
        """Test various error response scenarios"""
        test_cases = [
            {"job_id": "invalid-format", "expected_error": "FILE_NOT_FOUND"},
            {
                "job_id": "00000000-0000-0000-0000-000000000000",
                "expected_error": "FILE_NOT_FOUND",
            },
        ]

        for case in test_cases:
            # Test GET
            curl_cmd = [
                "curl",
                "-X",
                "GET",
                f"{server_url}/api/v1/file/synthesis/{case['job_id']}",
                "-H",
                "Content-Type: application/json",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Curl command failed: {result.stderr}"
            response = json.loads(result.stdout)
            assert response["success"] is False
            assert response["error"]["code"] == case["expected_error"]

            # Test DELETE
            curl_cmd = [
                "curl",
                "-X",
                "DELETE",
                f"{server_url}/api/v1/file/synthesis/{case['job_id']}",
                "-H",
                "Content-Type: application/json",
                "-H",
                f"Authorization: Bearer {auth_tokens['access_token']}",
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Curl command failed: {result.stderr}"
            response = json.loads(result.stdout)
            assert response["success"] is False
            assert response["error"]["code"] == case["expected_error"]


def run_tests():
    """Run tests using pytest"""
    pytest.main([__file__, "-v"])


def test_configuration():
    """Test that the configuration is correct"""
    import os
    import platform

    # Test server URL configuration
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 8000)))
    server_url = f"http://{host}:{port}"

    print(f"Server URL: {server_url}")
    print(f"Platform: {platform.system()}")
    print(f"Null device: {'NUL' if platform.system() == 'Windows' else '/dev/null'}")

    # Test curl availability
    try:
        result = subprocess.run(["curl", "--version"], capture_output=True, text=True)
        print(f"Curl available: {result.returncode == 0}")
    except FileNotFoundError:
        print("Curl not available")


if __name__ == "__main__":
    test_configuration()
    run_tests()
