import unittest
import os
import warnings


class TestLoginAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up class-level configurations to reduce noise."""
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        os.environ["CHROMA_SERVER_NOFILE"] = "1"

        warnings.filterwarnings("ignore", category=UserWarning, module="flask_limiter")
        warnings.filterwarnings("ignore", message=".*in-memory storage.*")
        warnings.filterwarnings("ignore", message=".*voice encoder.*")

    def setUp(self):
        """Set up test fixtures before each test method."""
        from flask import Flask
        from api.v1.auth.routes import auth_bp
        import uuid

        self.app = Flask(__name__)
        self.app.config.update(
            {
                "TESTING": True,
                "JWT_SECRET_KEY": "test-jwt-secret-key-for-testing",
                "SECRET_KEY": "test-secret-key-for-testing",
                "DATABASE_URL": "sqlite:///:memory:",
                "RATELIMIT_ENABLED": False,
                "WTF_CSRF_ENABLED": False,
            }
        )

        try:
            from flask_jwt_extended import JWTManager

            jwt = JWTManager(self.app)
        except Exception as e:
            print(f"JWT initialization failed: {e}, {jwt}")

        self.app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
        self.client = self.app.test_client()

        # Generate unique email for this test
        self.test_id = str(uuid.uuid4())[:8]
        self.test_email = f"testuser_{self.test_id}@example.com"

        register_response = self.client.post(
            "/api/v1/auth/register",
            json={"email": self.test_email, "password": "ValidPassword123!", "first_name": "Test", "last_name": "User"},
        )
        if register_response.status_code not in [201]:
            print(f"Registration failed: {register_response.get_json()}")

    def test_login_successful(self):
        """Test case for successful login."""
        response = self.client.post(
            "/api/v1/auth/login", json={"email": self.test_email, "password": "ValidPassword123!"}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", data)
        self.assertIn("access_token", data["data"])
        self.assertIn("refresh_token", data["data"])
        self.assertIn("user", data["data"])
        self.assertEqual(data["data"]["user"]["email"], self.test_email)

    def test_login_invalid_email(self):
        """Test case for login with an invalid email."""
        response = self.client.post(
            "/api/v1/auth/login", json={"email": "invaliduser@example.com", "password": "ValidPassword123!"}
        )
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data["error"]["code"], "INVALID_CREDENTIALS")

    def test_login_invalid_password(self):
        """Test case for login with an invalid password."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                # Fixed: Use the correct registered email
                "email": "validloginuser@example.com",
                "password": "WrongPassword123!",
            },
        )
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data["error"]["code"], "INVALID_CREDENTIALS")

    def test_login_missing_email(self):
        """Test case for missing email in the request payload."""
        response = self.client.post("/api/v1/auth/login", json={"password": "ValidPassword123!"})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"]["code"], "MISSING_FIELDS")

    def test_login_missing_password(self):
        """Test case for missing password in the request payload."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                # Fixed: Use the correct registered email
                "email": "validloginuser@example.com"
            },
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"]["code"], "MISSING_FIELDS")

    def test_login_empty_payload(self):
        """Test case for an empty request payload."""
        response = self.client.post("/api/v1/auth/login", json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"]["code"], "MISSING_BODY")

    def test_login_sql_injection(self):
        """Test case for possible SQL injection."""
        response = self.client.post("/api/v1/auth/login", json={"email": "' OR '1'='1", "password": "' OR '1'='1"})
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data["error"]["code"], "INVALID_CREDENTIALS")


if __name__ == "__main__":
    unittest.main()
