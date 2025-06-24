import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from backend.api.v1.auth.routes import auth_bp
from sqlalchemy.exc import IntegrityError


class TestRegister(unittest.TestCase):
    """Test cases for the register endpoint"""

    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        self.client = self.app.test_client()

    @patch('Voxify.backend.api.v1.auth.routes.get_database_manager')
    @patch('Voxify.backend.api.v1.auth.routes.hash_password')
    @patch('Voxify.backend.api.v1.auth.routes.validate_password_strength')
    @patch('Voxify.backend.api.v1.auth.routes.validate_email')
    def test_register_success(self, mock_validate_email, mock_validate_password, mock_hash_password, mock_db_manager):
        """Test successful registration"""
        # Mock email validation to pass
        mock_validate_email.return_value = (True, "")
        # Mock password validation to pass
        mock_validate_password.return_value = (True, "")
        # Mock password hashing
        mock_hash_password.return_value = "hashed_password"

        # Mock database session
        mock_session = MagicMock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        # Mock user creation to simulate returning a user object with .to_dict
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }

        # Patch the User creation
        with patch('Voxify.backend.api.v1.auth.routes.User', return_value=mock_user):
            response = self.client.post('/api/v1/auth/register', json={
                "email": "user@example.com",
                "password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe"
            })
            self.assertEqual(response.status_code, 201)
            data = response.get_json()
            self.assertEqual(data['message'], "User registered successfully")
            self.assertEqual(data['user']['email'], "user@example.com")

    def test_register_no_data(self):
        """Test registration with no data"""
        response = self.client.post(
            '/api/v1/auth/register',
            data='{}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data['error'], "No data provided")

    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        response = self.client.post('/api/v1/auth/register', json={
            "password": "SecurePassword123!"
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], "Email and password are required")

    @patch('Voxify.backend.api.v1.auth.routes.validate_email')
    def test_register_invalid_email(self, mock_validate_email):
        """Test registration with invalid email"""
        mock_validate_email.return_value = (False, "Invalid email format")
        response = self.client.post('/api/v1/auth/register', json={
            "email": "invalid-email",
            "password": "SecurePassword123!"
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], "Invalid email format")

    @patch('Voxify.backend.api.v1.auth.routes.validate_email')
    @patch('Voxify.backend.api.v1.auth.routes.validate_password_strength')
    def test_register_weak_password(self, mock_validate_password, mock_validate_email):
        """Test registration with weak password"""
        mock_validate_email.return_value = (True, "")
        mock_validate_password.return_value = (False, "Password must contain at least one uppercase letter")
        response = self.client.post('/api/v1/auth/register', json={
            "email": "user@example.com",
            "password": "weakpassword"
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], "Password must contain at least one uppercase letter")


    @patch('Voxify.backend.api.v1.auth.routes.get_database_manager')
    def test_register_email_already_exists(self, mock_db_manager):
        """Test registration with duplicate email"""
        mock_session = MagicMock()
        mock_session.commit.side_effect = IntegrityError("statement", "params", "orig")
        mock_db_manager.return_value.get_session.return_value = mock_session

        response = self.client.post('/api/v1/auth/register', json={
            "email": "duplicate@example.com",
            "password": "SecurePassword123!"
        })

        # 验证状态码为 409
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertEqual(data['error'], "Email already exists")

    @patch('Voxify.backend.api.v1.auth.routes.get_database_manager')
    def test_register_internal_error(self, mock_db_manager):
        """Test registration with server error"""
        # Simulate general exception during database interaction
        mock_session = MagicMock()
        mock_session.commit.side_effect = Exception("Database is down")
        mock_db_manager.return_value.get_session.return_value = mock_session

        response = self.client.post('/api/v1/auth/register', json={
            "email": "user@example.com",
            "password": "SecurePassword123!"
        })
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertEqual(data['error'], "Database is down")


if __name__ == "__main__":
    unittest.main()
