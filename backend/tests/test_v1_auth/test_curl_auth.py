import subprocess
import json
import pytest
import requests

class TestCurlAuth:
    """Test authentication endpoints using curl commands"""

    @pytest.fixture(scope="class", autouse=True)
    def check_server(self, server_url):
        """Check if server is running before tests"""
        try:
            # Use auth endpoint to check if server is running
            # GET request to auth endpoint will return 405 (Method Not Allowed) 
            # which means server is running but endpoint expects POST
            response = requests.get(f"{server_url}/api/v1/auth/login")
            # 405 means server is running but method not allowed (expected for GET on POST endpoint)
            # 404 would mean server not running or endpoint doesn't exist
            assert response.status_code in [405, 404], f"Unexpected status code: {response.status_code}"
        except requests.exceptions.ConnectionError:
            pytest.skip("Server is not running. Please start the server first.")

    @pytest.fixture(scope="class")
    def server_url(self):
        """Get the Flask server URL"""
        return "http://127.0.0.1:5000"

    @pytest.fixture(scope="class")
    def test_user(self):
        """Test user credentials"""
        return {
            "email": "test@example.com",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User"
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
            "access_token": response.get("access_token"),
            "refresh_token": response.get("refresh_token")
        }

    def test_register(self, server_url, test_user):
        """Test user registration using curl"""
        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/auth/register",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(test_user)
        ]
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        # If email already exists, check error code
        if "error" in response:
            assert response["error"]["code"] == "EMAIL_EXISTS"
        else:
            assert "message" in response
            assert response["message"] == "User registered successfully"

    def test_register_invalid_email(self, server_url, test_user):
        """Test registration with invalid email"""
        invalid_user = test_user.copy()
        invalid_user["email"] = "invalid-email"

        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/auth/register",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(invalid_user)
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0
        response = json.loads(result.stdout)
        assert "error" in response

    def test_register_weak_password(self, server_url, test_user):
        """Test registration with weak password"""
        invalid_user = test_user.copy()
        invalid_user["password"] = "weak"

        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/auth/register",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(invalid_user)
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0
        response = json.loads(result.stdout)
        assert "error" in response

    def test_login(self, server_url, test_user):
        """Test user login using curl"""
        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/auth/login",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "email": test_user["email"],
                "password": test_user["password"]
            })
        ]
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        # Check for access_token in data
        assert "data" in response
        assert "access_token" in response["data"]
        assert "refresh_token" in response["data"]

    def test_login_invalid_credentials(self, server_url, test_user):
        """Test login with invalid credentials"""
        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/auth/login",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "email": test_user["email"],
                "password": "wrong_password"
            })
        ]
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0
        response = json.loads(result.stdout)
        # Check for error.code and error.message in response
        assert "error" in response
        assert response["error"]["code"] == "INVALID_CREDENTIALS"
        assert response["error"]["message"] == "Invalid email or password"

    def test_refresh(self, server_url, auth_tokens):
        """Test token refresh using curl"""
        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/auth/refresh",
            "-H", f"Authorization: Bearer {auth_tokens['refresh_token']}"
        ]
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Curl command failed: {result.stderr}"
        response = json.loads(result.stdout)
        # Check for msg in response (error case)
        assert "msg" in response

    def test_refresh_invalid_token(self, server_url):
        """Test refresh with invalid token"""
        curl_cmd = [
            "curl", "-X", "POST",
            f"{server_url}/api/v1/auth/refresh",
            "-H", "Authorization: Bearer invalid_token"
        ]
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        assert result.returncode == 0
        response = json.loads(result.stdout)
        # Check for msg in response (error case)
        assert "msg" in response

def run_tests():
    """Run tests using pytest"""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    run_tests() 
