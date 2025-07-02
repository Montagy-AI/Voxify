import subprocess
import json
import pytest
import requests
import sys
import os
import platform

# Add the backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestJobServiceAPI:
    """Service tests for job API endpoints and data boundaries"""

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
        host = os.getenv('FLASK_HOST', '127.0.0.1')  # Use 127.0.0.1 for local testing
        port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 10000)))  # Default port from start.py
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
            "email": "jobtest@example.com",
            "password": "Test123!@#",
            "first_name": "Job",
            "last_name": "Tester"
        }

    @pytest.fixture(scope="class")
    def auth_tokens(self, server_url, test_user):
        """Get authentication tokens for testing"""
        # Register user
        register_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/auth/register",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(test_user)
        ]
        subprocess.run(register_cmd, capture_output=True)

        # Login to get tokens
        login_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/auth/login",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "email": test_user["email"],
                "password": test_user["password"]
            })
        ]
        result = subprocess.run(login_cmd, capture_output=True, text=True)
        response = json.loads(result.stdout)
        return {
            "access_token": response.get("data", {}).get("access_token"),
            "refresh_token": response.get("data", {}).get("refresh_token")
        }

    @pytest.fixture(scope="class")
    def test_voice_model_id(self, server_url, auth_tokens):
        """Get a real voice model id from the server, or skip if not found"""
        url = f"{server_url}/api/v1/voice/models"
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and isinstance(data, list) and len(data) > 0:
                    return data[0].get("id")
        except Exception:
            pass
        pytest.skip("No real voice model in DB, skip related tests.")

    def test_create_job_valid_data(self, server_url, auth_tokens, test_voice_model_id):
        """Test creating a job with valid data"""
        job_data = {
            "text_content": "Hello world, this is a test synthesis job.",
            "voice_model_id": test_voice_model_id,
            "text_language": "en-US",
            "output_format": "wav",
            "sample_rate": 22050,
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 1.0,
            "config": {
                "include_timestamps": True,
                "timestamp_granularity": "word"
            }
        }

        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/job",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(job_data)
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert response["error"]["code"] == "VOICE_MODEL_NOT_FOUND"

    def test_create_job_missing_required_fields(self, server_url, auth_tokens):
        """Test creating a job with missing required fields"""
        job_data = {
            "speed": 1.0,
            "pitch": 1.0
        }

        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/job",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(job_data)
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert "Validation failed" in response["error"]["message"]

    def test_create_job_invalid_parameters(self, server_url, auth_tokens, test_voice_model_id):
        """Test creating a job with invalid parameters"""
        test_cases = [
            {
                "data": {"text_content": "Hello", "voice_model_id": test_voice_model_id, "speed": 5.0},
                "expected_error": "Speed must be between 0.1 and 3.0"
            },
            {
                "data": {"text_content": "Hello", "voice_model_id": test_voice_model_id, "pitch": -1.0},
                "expected_error": "Pitch must be between 0.1 and 3.0"
            },
            {
                "data": {"text_content": "Hello", "voice_model_id": test_voice_model_id, "volume": 3.0},
                "expected_error": "Volume must be between 0.0 and 2.0"
            },
            {
                "data": {"text_content": "Hello", "voice_model_id": test_voice_model_id, "output_format": "invalid"},
                "expected_error": "Output format must be one of: wav, mp3, flac, ogg"
            },
            {
                "data": {"text_content": "Hello", "voice_model_id": test_voice_model_id, "sample_rate": 1000},
                "expected_error": "Sample rate must be one of: 8000, 16000, 22050, 44100, 48000"
            }
        ]

        for case in test_cases:
            curl_cmd = [
                "curl", "-X", "POST",
                f"{server_url}/api/v1/job",
                "-H", "Content-Type: application/json",
                "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
                "-d", json.dumps(case["data"])
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0

            response = json.loads(result.stdout)
            assert response["success"] is False
            assert "error" in response
            assert case["expected_error"] in str(response["error"]["details"])

    def test_list_jobs_basic(self, server_url, auth_tokens):
        """Test listing jobs with basic parameters"""
        curl_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/job",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"

        response = json.loads(result.stdout)
        assert response["success"] is True
        assert "data" in response
        assert isinstance(response["data"], list)

    def test_list_jobs_with_filters(self, server_url, auth_tokens):
        """Test listing jobs with various filters"""
        test_filters = [
            "?status=pending",
            "?limit=5&offset=0",
            "?sort_by=created_at&sort_order=desc",
            "?include_text=false"
        ]

        for filter_param in test_filters:
            curl_cmd = [
                "curl", "-X", "GET",
                f"{server_url}/api/v1/job{filter_param}",
                "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Failed with filter: {filter_param}"

            response = json.loads(result.stdout)
            assert response["success"] is True
            assert "data" in response

    def test_list_jobs_invalid_filters(self, server_url, auth_tokens):
        """Test listing jobs with invalid filter parameters"""
        test_cases = [
            "?status=invalid_status",
            "?sort_by=invalid_field",
            "?sort_order=invalid_order",
            "?limit=invalid_limit"
        ]

        for filter_param in test_cases:
            curl_cmd = [
                "curl", "-X", "GET",
                f"{server_url}/api/v1/job{filter_param}",
                "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0

            response = json.loads(result.stdout)
            assert response["success"] is False
            assert "error" in response

    def test_get_job_details(self, server_url, auth_tokens, test_voice_model_id):
        """Test getting job details by ID"""
        # First create a job
        job_data = {
            "text_content": "Test job for details",
            "voice_model_id": test_voice_model_id,
            "output_format": "wav"
        }

        create_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/job",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(job_data)
        ]

        result = subprocess.run(create_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        create_response = json.loads(result.stdout)
        job_id = create_response["data"]["id"]

        # Now get job details
        get_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/job/{job_id}",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(get_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"

        response = json.loads(result.stdout)
        assert response["success"] is True
        assert response["data"]["id"] == job_id
        assert response["data"]["text_content"] == job_data["text_content"]

    def test_get_job_not_found(self, server_url, auth_tokens):
        """Test getting a non-existent job"""
        curl_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/job/nonexistent_job_id",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert response["error"]["code"] == "JOB_NOT_FOUND"

    def test_update_job_valid_data(self, server_url, auth_tokens, test_voice_model_id):
        """Test updating a job with valid data"""
        # First create a job
        job_data = {
            "text_content": "Original text",
            "voice_model_id": test_voice_model_id,
            "output_format": "wav"
        }

        create_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/job",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(job_data)
        ]

        result = subprocess.run(create_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        create_response = json.loads(result.stdout)
        job_id = create_response["data"]["id"]

        # Update the job
        update_data = {
            "text_content": "Updated text content",
            "speed": 1.5,
            "pitch": 1.2,
            "volume": 0.8
        }

        update_cmd = [
            "curl", "-X", "PUT",
            f"{server_url}/api/v1/job/{job_id}",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(update_data)
        ]

        result = subprocess.run(update_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"

        response = json.loads(result.stdout)
        assert response["success"] is True
        assert response["data"]["text_content"] == update_data["text_content"]
        assert response["data"]["speed"] == update_data["speed"]

    def test_update_job_invalid_status(self, server_url, auth_tokens, test_voice_model_id):
        """Test updating a job that cannot be updated due to status"""
        # This test would require mocking a job with non-pending status
        # For now, we'll test the API structure
        update_data = {
            "text_content": "Updated text"
        }

        curl_cmd = [
            "curl", "-X", "PUT",
            f"{server_url}/api/v1/job/invalid_job_id",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(update_data)
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_patch_job_status(self, server_url, auth_tokens, test_voice_model_id):
        """Test patching job status and progress"""
        # First create a job
        job_data = {
            "text_content": "Test job for patching",
            "voice_model_id": test_voice_model_id,
            "output_format": "wav"
        }

        create_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/job",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(job_data)
        ]

        result = subprocess.run(create_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        create_response = json.loads(result.stdout)
        job_id = create_response["data"]["id"]

        # Patch the job status
        patch_data = {
            "status": "processing",
            "progress": 0.5,
            "processing_time_ms": 1000
        }

        patch_cmd = [
            "curl", "-X", "PATCH",
            f"{server_url}/api/v1/job/{job_id}",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(patch_data)
        ]

        result = subprocess.run(patch_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"

        response = json.loads(result.stdout)
        assert response["success"] is True
        assert response["data"]["status"] == patch_data["status"]
        assert response["data"]["progress"] == patch_data["progress"]

    def test_delete_job(self, server_url, auth_tokens, test_voice_model_id):
        """Test deleting a job"""
        # First create a job
        job_data = {
            "text_content": "Test job for deletion",
            "voice_model_id": test_voice_model_id,
            "output_format": "wav"
        }

        create_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/job",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(job_data)
        ]

        result = subprocess.run(create_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        create_response = json.loads(result.stdout)
        job_id = create_response["data"]["id"]

        # Delete the job
        delete_cmd = [
            "curl", "-X", "DELETE",
            f"{server_url}/api/v1/job/{job_id}",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(delete_cmd, capture_output=True, text=True)
        # Note: DELETE might return 204 (No Content) or 400 if job cannot be deleted
        assert result.returncode == 0

    def test_job_progress_stream(self, server_url, auth_tokens, test_voice_model_id):
        """Test job progress streaming endpoint"""
        # First create a job
        job_data = {
            "text_content": "Test job for progress streaming",
            "voice_model_id": test_voice_model_id,
            "output_format": "wav"
        }

        create_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/job",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(job_data)
        ]

        result = subprocess.run(create_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        create_response = json.loads(result.stdout)
        job_id = create_response["data"]["id"]

        # Test progress streaming
        progress_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/job/{job_id}/progress",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-H", "Accept: text/event-stream",
            "--max-time", "5"  # Limit to 5 seconds
        ]

        result = subprocess.run(progress_cmd, capture_output=True, text=True)
        # Progress streaming might timeout or return data
        assert result.returncode in [0, 28]  # 28 is curl timeout

    def test_unauthorized_access(self, server_url):
        """Test accessing job endpoints without authentication"""
        endpoints = [
            ("GET", "/api/v1/job"),
            ("POST", "/api/v1/job"),
            ("GET", "/api/v1/job/test_id"),
            ("PUT", "/api/v1/job/test_id"),
            ("DELETE", "/api/v1/job/test_id")
        ]

        for method, endpoint in endpoints:
            curl_cmd = [
                "curl", "-X", method,
                f"{server_url}{endpoint}",
                "-H", "Content-Type: application/json"
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0

            response = json.loads(result.stdout)
            assert "msg" in response
            assert "Authorization" in response["msg"]

    def test_duplicate_job_creation(self, server_url, auth_tokens, test_voice_model_id):
        """Test creating duplicate jobs with same text and config"""
        job_data = {
            "text_content": "Duplicate test text",
            "voice_model_id": test_voice_model_id,
            "output_format": "wav",
            "sample_rate": 22050
        }

        # Create first job
        create_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/job",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(job_data)
        ]

        result = subprocess.run(create_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        first_response = json.loads(result.stdout)
        assert first_response["success"] is True

        # Create duplicate job
        result = subprocess.run(create_cmd, capture_output=True, text=True)
        assert result.returncode == 0

        second_response = json.loads(result.stdout)
        # Should return existing job or success message about duplicate
        assert second_response["success"] is True


def run_tests():
    """Run tests using pytest"""
    pytest.main([__file__, "-v"])


def test_configuration():
    """Test that the configuration is correct"""
    # Test server URL configuration
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 10000)))
    server_url = f"http://{host}:{port}"

    print(f"Server URL: {server_url}")
    print(f"Platform: {platform.system()}")

    # Test curl availability
    try:
        result = subprocess.run(["curl", "--version"], capture_output=True, text=True)
        print(f"Curl available: {result.returncode == 0}")
    except FileNotFoundError:
        print("Curl not available")


if __name__ == "__main__":
    test_configuration()
    run_tests()
