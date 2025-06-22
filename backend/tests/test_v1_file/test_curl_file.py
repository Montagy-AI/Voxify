import subprocess
import json
import pytest
import requests
import time
from unittest.mock import patch
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

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
        """Get the Flask server URL"""
        return "http://127.0.0.1:5000"

    @pytest.fixture(scope="class")
    def test_user(self):
        """Test user credentials"""
        return {
            "email": "filetest@example.com",
            "password": "Test123!@#",
            "first_name": "File",
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
    def test_job_id(self, server_url, auth_tokens):
        """Create a test synthesis job and return its ID"""
        # Create a test job
        job_data = {
            "text_content": "Hello, this is a test for file download.",
            "voice_model_id": "test-voice-model",
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 1.0,
            "output_format": "wav",
            "sample_rate": 44100
        }
        
        job_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/job",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-d", json.dumps(job_data)
        ]
        
        result = subprocess.run(job_cmd, capture_output=True, text=True)
        response = json.loads(result.stdout)
        return response.get("data", {}).get("id")

    def test_download_synthesis_file_without_auth(self, server_url):
        """Test download synthesis file without authentication"""
        curl_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H", "Content-Type: application/json"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 401 Unauthorized
        assert "Missing Authorization Header" in result.stdout

    def test_download_synthesis_file_invalid_job_id(self, server_url, auth_tokens):
        """Test download synthesis file with invalid job ID"""
        curl_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/file/synthesis/invalid-job-id",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
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
            "curl", "-X", "GET",
            f"{server_url}/api/v1/file/synthesis/00000000-0000-0000-0000-000000000000",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response
        assert response["error"]["code"] == "FILE_NOT_FOUND"

    def test_download_synthesis_file_with_valid_job(self, server_url, auth_tokens, test_job_id):
        """Test download synthesis file with valid job ID"""
        if not test_job_id:
            pytest.skip("No test job ID available")
            
        curl_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/file/synthesis/{test_job_id}",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-o", "/dev/null",  # Don't save the file, just check response
            "-w", "%{http_code}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 404 if file doesn't exist yet, or 200 if it does
        status_code = result.stdout.strip()
        assert status_code in ["200", "404"]

    def test_delete_synthesis_file_without_auth(self, server_url):
        """Test delete synthesis file without authentication"""
        curl_cmd = [
            "curl", "-X", "DELETE",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H", "Content-Type: application/json"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 401 Unauthorized
        assert "Missing Authorization Header" in result.stdout

    def test_delete_synthesis_file_invalid_job_id(self, server_url, auth_tokens):
        """Test delete synthesis file with invalid job ID"""
        curl_cmd = [
            "curl", "-X", "DELETE",
            f"{server_url}/api/v1/file/synthesis/invalid-job-id",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
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
            "curl", "-X", "DELETE",
            f"{server_url}/api/v1/file/synthesis/00000000-0000-0000-0000-000000000000",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
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
            "curl", "-X", "DELETE",
            f"{server_url}/api/v1/file/synthesis/{test_job_id}",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        # Should return success even if file doesn't exist
        assert response["success"] is True

    def test_download_synthesis_file_with_invalid_token(self, server_url):
        """Test download synthesis file with invalid token"""
        curl_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H", "Content-Type: application/json",
            "-H", "Authorization: Bearer invalid_token_here"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 401 Unauthorized
        assert "Not enough segments" in result.stdout

    def test_delete_synthesis_file_with_invalid_token(self, server_url):
        """Test delete synthesis file with invalid token"""
        curl_cmd = [
            "curl", "-X", "DELETE",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H", "Content-Type: application/json",
            "-H", "Authorization: Bearer invalid_token_here"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 401 Unauthorized
        assert "Not enough segments" in result.stdout

    def test_download_synthesis_file_malformed_job_id(self, server_url, auth_tokens):
        """Test download synthesis file with malformed job ID"""
        curl_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/file/synthesis/not-a-uuid",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_delete_synthesis_file_malformed_job_id(self, server_url, auth_tokens):
        """Test delete synthesis file with malformed job ID"""
        curl_cmd = [
            "curl", "-X", "DELETE",
            f"{server_url}/api/v1/file/synthesis/not-a-uuid",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_download_synthesis_file_wrong_method(self, server_url, auth_tokens):
        """Test download synthesis file with wrong HTTP method"""
        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 405 Method Not Allowed
        assert "405" in result.stdout or "Method Not Allowed" in result.stdout

    def test_delete_synthesis_file_wrong_method(self, server_url, auth_tokens):
        """Test delete synthesis file with wrong HTTP method"""
        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/file/synthesis/test-job-id",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        # Should return 405 Method Not Allowed
        assert "405" in result.stdout or "Method Not Allowed" in result.stdout

    def test_download_synthesis_file_with_headers(self, server_url, auth_tokens, test_job_id):
        """Test download synthesis file with additional headers"""
        if not test_job_id:
            pytest.skip("No test job ID available")
            
        curl_cmd = [
            "curl", "-X", "GET",
            f"{server_url}/api/v1/file/synthesis/{test_job_id}",
            "-H", "Content-Type: application/json",
            "-H", "Accept: audio/*",
            "-H", f"Authorization: Bearer {auth_tokens['access_token']}",
            "-o", "/dev/null",
            "-w", "%{http_code}"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        status_code = result.stdout.strip()
        assert status_code in ["200", "404"]

    def test_unauthorized_access(self, server_url):
        """Test unauthorized access to file endpoints"""
        test_endpoints = [
            "/api/v1/file/synthesis/test-job-id",
            "/api/v1/file/synthesis/00000000-0000-0000-0000-000000000000"
        ]
        
        for endpoint in test_endpoints:
            # Test GET without auth
            curl_cmd = [
                "curl", "-X", "GET",
                f"{server_url}{endpoint}",
                "-H", "Content-Type: application/json"
            ]
            
            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Curl command failed: {result.stderr}"
            assert "Missing Authorization Header" in result.stdout
            
            # Test DELETE without auth
            curl_cmd = [
                "curl", "-X", "DELETE",
                f"{server_url}{endpoint}",
                "-H", "Content-Type: application/json"
            ]
            
            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Curl command failed: {result.stderr}"
            assert "Missing Authorization Header" in result.stdout

    def test_file_endpoint_error_responses(self, server_url, auth_tokens):
        """Test various error response scenarios"""
        test_cases = [
            {
                "job_id": "invalid-format",
                "expected_error": "FILE_NOT_FOUND"
            },
            {
                "job_id": "00000000-0000-0000-0000-000000000000",
                "expected_error": "FILE_NOT_FOUND"
            }
        ]
        
        for case in test_cases:
            # Test GET
            curl_cmd = [
                "curl", "-X", "GET",
                f"{server_url}/api/v1/file/synthesis/{case['job_id']}",
                "-H", "Content-Type: application/json",
                "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
            ]
            
            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Curl command failed: {result.stderr}"
            response = json.loads(result.stdout)
            assert response["success"] is False
            assert response["error"]["code"] == case["expected_error"]
            
            # Test DELETE
            curl_cmd = [
                "curl", "-X", "DELETE",
                f"{server_url}/api/v1/file/synthesis/{case['job_id']}",
                "-H", "Content-Type: application/json",
                "-H", f"Authorization: Bearer {auth_tokens['access_token']}"
            ]
            
            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Curl command failed: {result.stderr}"
            response = json.loads(result.stdout)
            assert response["success"] is False
            assert response["error"]["code"] == case["expected_error"]


def run_tests():
    """Run tests using pytest"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests() 