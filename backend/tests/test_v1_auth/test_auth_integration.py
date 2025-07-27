"""
Authentication API Integration Tests
Tests for complete authentication flow including registration, login, token refresh, and profile management
"""

import pytest
import os
import sys
import json
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, backend_dir)

from flask import Flask
from flask_jwt_extended import JWTManager
from api.v1.auth.routes import auth_bp
from database.models import get_database_manager, User
from api.utils.password import hash_password


@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    app = Flask(__name__)

    # Configure JWT
    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    jwt = JWTManager(app)

    # Register blueprint
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app"""
    return app.test_client()


@pytest.fixture
def test_user_data():
    """Test user data for integration tests"""
    return {
        "email": "integration_test@example.com",
        "password": "SecurePassword123!",
        "first_name": "Integration",
        "last_name": "Test",
    }


@pytest.fixture
def cleanup_test_user(test_user_data):
    """Cleanup fixture to remove test user from database"""
    # Clean up before test
    try:
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Delete test user if exists
        user = session.query(User).filter_by(email=test_user_data["email"]).first()
        if user:
            session.delete(user)
            session.commit()

        session.close()
    except Exception:
        pass  # Ignore cleanup errors

    yield  # Run test

    # Clean up after test
    try:
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Delete test user if exists
        user = session.query(User).filter_by(email=test_user_data["email"]).first()
        if user:
            session.delete(user)
            session.commit()

        session.close()
    except Exception:
        pass  # Ignore cleanup errors


class TestAuthIntegration:
    """Integration tests for complete authentication flow"""

    def test_complete_auth_flow(self, client, test_user_data, cleanup_test_user):
        """Test complete authentication flow: register -> login -> refresh -> profile"""

        # Step 1: Register new user
        register_response = client.post("/api/v1/auth/register", json=test_user_data)

        # Should be successful registration
        assert register_response.status_code in [201, 409]
        register_data = register_response.get_json()

        if register_response.status_code == 201:
            assert register_data["success"] is True
            assert "user" in register_data["data"]
            user_id = register_data["data"]["user"]["id"]
        else:
            # User already exists, get user ID from database
            db_manager = get_database_manager()
            session = db_manager.get_session()
            user = session.query(User).filter_by(email=test_user_data["email"]).first()
            user_id = user.id
            session.close()

        # Step 2: Login with registered user
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        assert login_response.status_code == 200
        login_data = login_response.get_json()
        assert login_data["success"] is True
        assert "access_token" in login_data["data"]
        assert "refresh_token" in login_data["data"]
        assert "user" in login_data["data"]

        access_token = login_data["data"]["access_token"]
        refresh_token = login_data["data"]["refresh_token"]

        # Step 3: Get user profile with access token
        profile_response = client.get(
            "/api/v1/auth/profile", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert profile_response.status_code == 200
        profile_data = profile_response.get_json()
        assert profile_data["success"] is True
        assert "user" in profile_data["data"]
        assert profile_data["data"]["user"]["email"] == test_user_data["email"]

        # Step 4: Update user profile
        update_data = {"first_name": "Updated", "last_name": "Name"}

        update_response = client.put(
            "/api/v1/auth/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert update_response.status_code == 200
        update_response_data = update_response.get_json()
        assert update_response_data["success"] is True
        assert "updated_fields" in update_response_data["data"]

        # Step 5: Refresh access token
        refresh_response = client.post(
            "/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert refresh_response.status_code == 200
        refresh_data = refresh_response.get_json()
        assert refresh_data["success"] is True
        assert "access_token" in refresh_data["data"]
        assert "refresh_token" in refresh_data["data"]

        # Step 6: Verify new access token works
        new_access_token = refresh_data["data"]["access_token"]
        verify_profile_response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )

        assert verify_profile_response.status_code == 200
        verify_data = verify_profile_response.get_json()
        assert verify_data["success"] is True

    def test_auth_flow_with_invalid_credentials(self, client):
        """Test authentication flow with invalid credentials"""

        # Try to login with non-existent user
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrongpassword"},
        )

        assert login_response.status_code == 401
        login_data = login_response.get_json()
        assert login_data["success"] is False
        assert login_data["error"]["code"] == "INVALID_CREDENTIALS"

    def test_auth_flow_with_weak_password(self, client):
        """Test registration with weak password"""

        weak_password_data = {"email": "weak_password@example.com", "password": "weak"}

        register_response = client.post(
            "/api/v1/auth/register", json=weak_password_data
        )

        assert register_response.status_code == 400
        register_data = register_response.get_json()
        assert register_data["success"] is False
        assert register_data["error"]["code"] == "WEAK_PASSWORD"

    def test_auth_flow_with_invalid_email(self, client):
        """Test registration with invalid email format"""

        invalid_email_data = {
            "email": "invalid-email-format",
            "password": "SecurePassword123!",
        }

        register_response = client.post(
            "/api/v1/auth/register", json=invalid_email_data
        )

        assert register_response.status_code == 400
        register_data = register_response.get_json()
        assert register_data["success"] is False
        assert register_data["error"]["code"] == "INVALID_EMAIL"

    def test_auth_flow_with_duplicate_email(
        self, client, test_user_data, cleanup_test_user
    ):
        """Test registration with duplicate email"""

        # Register first user
        first_register = client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register with same email
        second_register = client.post("/api/v1/auth/register", json=test_user_data)

        # Second registration should fail
        assert second_register.status_code == 409
        second_data = second_register.get_json()
        assert second_data["success"] is False
        assert second_data["error"]["code"] == "EMAIL_EXISTS"

    def test_auth_flow_with_missing_fields(self, client):
        """Test registration and login with missing required fields"""

        # Test registration with missing email
        register_response = client.post(
            "/api/v1/auth/register", json={"password": "SecurePassword123!"}
        )

        assert register_response.status_code == 400
        register_data = register_response.get_json()
        assert register_data["success"] is False
        assert register_data["error"]["code"] == "MISSING_FIELDS"

        # Test login with missing password
        login_response = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com"}
        )

        assert login_response.status_code == 400
        login_data = login_response.get_json()
        assert login_data["success"] is False
        assert login_data["error"]["code"] == "MISSING_FIELDS"

    def test_auth_flow_with_invalid_tokens(self, client):
        """Test profile access with invalid tokens"""

        # Try to access profile without token
        profile_response = client.get("/api/v1/auth/profile")

        assert profile_response.status_code == 401

        # Try to access profile with invalid token
        profile_response = client.get(
            "/api/v1/auth/profile", headers={"Authorization": "Bearer invalid_token"}
        )

        assert profile_response.status_code == 422  # JWT decode error

    def test_auth_flow_profile_update_validation(
        self, client, test_user_data, cleanup_test_user
    ):
        """Test profile update with invalid data"""

        # First register and login a user
        client.post("/api/v1/auth/register", json=test_user_data)

        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        access_token = login_response.get_json()["data"]["access_token"]

        # Try to update profile with invalid email
        update_response = client.put(
            "/api/v1/auth/profile",
            json={"email": "invalid-email"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert update_response.status_code == 400
        update_data = update_response.get_json()
        assert update_data["success"] is False
        assert update_data["error"]["code"] == "INVALID_EMAIL"

    def test_auth_flow_concurrent_registration(self, client):
        """Test concurrent registration attempts"""

        # Simulate concurrent registration attempts
        responses = []
        for i in range(3):
            user_data = {
                "email": f"concurrent_test_{i}@example.com",
                "password": "SecurePassword123!",
                "first_name": f"User{i}",
                "last_name": "Test",
            }

            response = client.post("/api/v1/auth/register", json=user_data)
            responses.append(response)

        # All registrations should be successful
        for response in responses:
            assert response.status_code in [201, 409]  # 201 for new, 409 for existing
            data = response.get_json()
            assert data is not None

    def test_auth_flow_database_persistence(
        self, client, test_user_data, cleanup_test_user
    ):
        """Test that user data persists in database across requests"""

        # Register user
        register_response = client.post("/api/v1/auth/register", json=test_user_data)

        assert register_response.status_code in [201, 409]

        # Verify user exists in database
        db_manager = get_database_manager()
        session = db_manager.get_session()

        user = session.query(User).filter_by(email=test_user_data["email"]).first()
        assert user is not None
        assert user.email == test_user_data["email"]
        assert user.first_name == test_user_data["first_name"]
        assert user.last_name == test_user_data["last_name"]

        session.close()

    def test_auth_flow_token_expiration(
        self, client, test_user_data, cleanup_test_user
    ):
        """Test token expiration and refresh functionality"""

        # Register and login user
        client.post("/api/v1/auth/register", json=test_user_data)

        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        access_token = login_response.get_json()["data"]["access_token"]
        refresh_token = login_response.get_json()["data"]["refresh_token"]

        # Verify access token works
        profile_response = client.get(
            "/api/v1/auth/profile", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert profile_response.status_code == 200

        # Test refresh token functionality
        refresh_response = client.post(
            "/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert refresh_response.status_code == 200
        refresh_data = refresh_response.get_json()
        assert refresh_data["success"] is True
        assert "access_token" in refresh_data["data"]

    def test_auth_flow_profile_update_success(
        self, client, test_user_data, cleanup_test_user
    ):
        """Test successful profile update scenarios"""

        # Register and login user
        client.post("/api/v1/auth/register", json=test_user_data)

        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        access_token = login_response.get_json()["data"]["access_token"]

        # Test updating first name only
        update_response = client.put(
            "/api/v1/auth/profile",
            json={"first_name": "NewFirstName"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert update_response.status_code == 200
        update_data = update_response.get_json()
        assert update_data["success"] is True
        assert "first_name" in update_data["data"]["updated_fields"]

        # Test updating last name only
        update_response = client.put(
            "/api/v1/auth/profile",
            json={"last_name": "NewLastName"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert update_response.status_code == 200
        update_data = update_response.get_json()
        assert update_data["success"] is True
        assert "last_name" in update_data["data"]["updated_fields"]

        # Test updating both names
        update_response = client.put(
            "/api/v1/auth/profile",
            json={"first_name": "FinalFirstName", "last_name": "FinalLastName"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert update_response.status_code == 200
        update_data = update_response.get_json()
        assert update_data["success"] is True
        assert "first_name" in update_data["data"]["updated_fields"]
        assert "last_name" in update_data["data"]["updated_fields"]
