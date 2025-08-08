import unittest
import requests
import os
import pytest


class TestLoginAPI(unittest.TestCase):
    """Test cases for the login API endpoint"""

    @classmethod
    def setUpClass(cls):
        """Set up test configuration based on environment"""
        host = os.getenv("FLASK_HOST", "127.0.0.1")
        port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 8000)))
        cls.BASE_URL = f"http://{host}:{port}/api/v1/auth/login"
        cls.HEADERS = {"Content-Type": "application/json"}

        cls.is_docker = os.getenv("DOCKER_ENV", "false").lower() == "true"

    def post_login(self, payload):
        """Helper method to send a POST request"""
        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.HEADERS, timeout=30)
            return response
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

    # TODO: Uncomment and implement this test after registering a user
    # def test_login_successful(self):
    #     """Test case for successful login."""
    #     payload = {
    #         "email": "duplicate1@example.com",
    #         "password": "SecurePassword123!"
    #     }
    #     response = self.post_login(payload)
    #     self.assertEqual(response.status_code, 200)
    #     data = response.json()
    #     self.assertIn("access_token", data)
    #     self.assertIn("refresh_token", data)
    #     self.assertIn("user", data)
    #     self.assertEqual(data["user"]["email"], payload["email"])

    def test_login_invalid_email(self):
        """Test case for login with an invalid email."""
        payload = {"email": "invaliduser@example.com", "password": "ValidPassword123!"}
        response = self.post_login(payload)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error"]["code"], "INVALID_CREDENTIALS")

    def test_login_invalid_password(self):
        """Test case for login with an invalid password."""
        payload = {"email": "validuser@example.com", "password": "WrongPassword123!"}
        response = self.post_login(payload)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error"]["code"], "INVALID_CREDENTIALS")

    def test_login_missing_email(self):
        """Test case for missing email in the request payload."""
        payload = {"password": "ValidPassword123!"}
        response = self.post_login(payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"]["code"], "MISSING_FIELDS")

    def test_login_missing_password(self):
        """Test case for missing password in the request payload."""
        payload = {"email": "validuser@example.com"}
        response = self.post_login(payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"]["code"], "MISSING_FIELDS")

    def test_login_empty_payload(self):
        """Test case for an empty request payload."""
        payload = {}
        response = self.post_login(payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"]["code"], "MISSING_BODY")

    def test_login_sql_injection(self):
        """Test case for possible SQL injection."""
        payload = {"email": "' OR '1'='1", "password": "' OR '1'='1"}
        response = self.post_login(payload)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error"]["code"], "INVALID_CREDENTIALS")

    def test_login_malformed_json(self):
        """Test case for malformed JSON payload."""
        try:
            response = requests.post(self.BASE_URL, data="invalid json", headers=self.HEADERS, timeout=30)
            self.assertEqual(response.status_code, 400)
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

    def test_login_wrong_content_type(self):
        """Test case for wrong content type."""
        payload = {"email": "test@example.com", "password": "password123"}
        headers = {"Content-Type": "text/plain"}
        try:
            response = requests.post(self.BASE_URL, json=payload, headers=headers, timeout=30)
            self.assertIn(response.status_code, [400, 401, 415])
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

    def test_server_connectivity(self):
        """Test that we can connect to the server (debugging test)"""
        try:
            response = requests.get(self.BASE_URL, timeout=10)
            # Should get 405 Method Not Allowed for GET on login endpoint
            self.assertEqual(response.status_code, 405)
        except requests.exceptions.ConnectionError as e:
            self.fail(f"❌ Cannot connect to API server at {self.BASE_URL}: {e}")
        except requests.exceptions.RequestException as e:
            # Other request errors are okay, we just want to test connectivity
            print(f"✅ Connected to server, got expected error: {e}")


class TestLoginAPIPytest:
    """Pytest version of login API tests"""

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        """Setup for pytest"""
        host = os.getenv("FLASK_HOST", "127.0.0.1")
        port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 8000)))
        self.base_url = f"http://{host}:{port}/api/v1/auth/login"
        self.headers = {"Content-Type": "application/json"}

        # Check server availability
        try:
            health_url = f"http://{host}:{port}/health"
            response = requests.get(health_url, timeout=5)
            if response.status_code != 200:
                pytest.skip("API server is not healthy")
        except requests.exceptions.RequestException:
            pytest.skip("Cannot connect to API server")

    def post_login(self, payload):
        """Helper method for pytest"""
        return requests.post(self.base_url, json=payload, headers=self.headers, timeout=30)


def run_tests():
    """Run tests using unittest"""
    unittest.main(verbosity=2)


def test_configuration():
    """Test configuration for debugging"""
    import platform

    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = os.getenv("FLASK_PORT", "8000")
    docker_env = os.getenv("DOCKER_ENV", "false")

    print("Login API Test Configuration:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Docker: {docker_env}")
    print(f"  Target URL: http://{host}:{port}/api/v1/auth/login")
    print(f"  Platform: {platform.system()}")

    # Test basic connectivity
    try:
        response = requests.get(f"http://{host}:{port}/health", timeout=5)
        print(f"  Health Check: {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")
    except Exception as e:
        print(f"  Health Check: ❌ FAIL - {e}")


if __name__ == "__main__":
    test_configuration()
    run_tests()
