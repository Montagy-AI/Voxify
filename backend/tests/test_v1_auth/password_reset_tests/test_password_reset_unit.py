"""
Unit tests for password reset functionality
Tests for password reset utility functions and email service
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import uuid
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Import functions to test
from api.utils.password import (
    generate_reset_token,
    is_reset_token_valid,
    get_reset_token_expiry,
)
from api.utils.email_service import EmailService


class TestPasswordResetUtils(unittest.TestCase):
    """Test password reset utility functions"""

    def test_generate_reset_token(self):
        """Test reset token generation"""
        # Generate token
        token = generate_reset_token()

        # Verify token is a string
        self.assertIsInstance(token, str)

        # Verify token is not empty
        self.assertTrue(len(token) > 0)

        # Verify token is valid UUID format
        try:
            uuid.UUID(token)
        except ValueError:
            self.fail("Generated token is not a valid UUID")

        # Verify tokens are unique
        token2 = generate_reset_token()
        self.assertNotEqual(token, token2)

    def test_get_reset_token_expiry(self):
        """Test reset token expiry generation"""
        # Get expiry time
        expiry = get_reset_token_expiry()

        # Verify it's a datetime
        self.assertIsInstance(expiry, datetime)

        # Verify it's in the future
        now = datetime.utcnow()
        self.assertGreater(expiry, now)

        # Verify it's approximately 15 minutes from now (allow 1 second tolerance)
        expected_expiry = now + timedelta(minutes=15)
        time_diff = abs((expiry - expected_expiry).total_seconds())
        self.assertLess(time_diff, 1)

    def test_is_reset_token_valid_success(self):
        """Test valid token validation"""
        token = "test-token-123"
        stored_token = "test-token-123"
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        is_valid, error_message = is_reset_token_valid(token, stored_token, expires_at)

        self.assertTrue(is_valid)
        self.assertEqual(error_message, "")

    def test_is_reset_token_valid_empty_token(self):
        """Test validation with empty token"""
        token = ""
        stored_token = "test-token-123"
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        is_valid, error_message = is_reset_token_valid(token, stored_token, expires_at)

        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Invalid reset token")

    def test_is_reset_token_valid_empty_stored_token(self):
        """Test validation with empty stored token"""
        token = "test-token-123"
        stored_token = ""
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        is_valid, error_message = is_reset_token_valid(token, stored_token, expires_at)

        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Invalid reset token")

    def test_is_reset_token_valid_mismatched_tokens(self):
        """Test validation with mismatched tokens"""
        token = "test-token-123"
        stored_token = "different-token-456"
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        is_valid, error_message = is_reset_token_valid(token, stored_token, expires_at)

        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Invalid reset token")

    def test_is_reset_token_valid_expired_token(self):
        """Test validation with expired token"""
        token = "test-token-123"
        stored_token = "test-token-123"
        expires_at = datetime.utcnow() - timedelta(minutes=1)  # Expired 1 minute ago

        is_valid, error_message = is_reset_token_valid(token, stored_token, expires_at)

        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Reset token has expired")

    def test_is_reset_token_valid_no_expiry(self):
        """Test validation with no expiry time"""
        token = "test-token-123"
        stored_token = "test-token-123"
        expires_at = None

        is_valid, error_message = is_reset_token_valid(token, stored_token, expires_at)

        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Reset token has expired")


class TestEmailService(unittest.TestCase):
    """Test email service functionality"""

    def setUp(self):
        """Set up test environment"""
        # Create email service with test configuration
        self.test_config = {
            "host": "smtp.test.com",
            "port": 587,
            "username": "test@example.com",
            "password": "testpass",
            "use_tls": True,
            "from_email": "noreply@voxify.com",
            "from_name": "Voxify Test",
        }
        self.email_service = EmailService(self.test_config)

    def test_email_service_init_with_config(self):
        """Test email service initialization with config"""
        self.assertEqual(self.email_service.smtp_host, "smtp.test.com")
        self.assertEqual(self.email_service.smtp_port, 587)
        self.assertEqual(self.email_service.smtp_username, "test@example.com")
        self.assertEqual(self.email_service.smtp_password, "testpass")
        self.assertTrue(self.email_service.smtp_use_tls)
        self.assertEqual(self.email_service.from_email, "noreply@voxify.com")
        self.assertEqual(self.email_service.from_name, "Voxify Test")

    @patch.dict(
        "os.environ",
        {
            "SMTP_HOST": "smtp.env.com",
            "SMTP_PORT": "465",
            "SMTP_USERNAME": "env@example.com",
            "SMTP_PASSWORD": "envpass",
            "SMTP_USE_TLS": "false",
            "SMTP_FROM_EMAIL": "env-noreply@voxify.com",
            "SMTP_FROM_NAME": "Voxify Env",
        },
    )
    def test_email_service_init_with_env_vars(self):
        """Test email service initialization with environment variables"""
        email_service = EmailService()

        self.assertEqual(email_service.smtp_host, "smtp.env.com")
        self.assertEqual(email_service.smtp_port, 465)
        self.assertEqual(email_service.smtp_username, "env@example.com")
        self.assertEqual(email_service.smtp_password, "envpass")
        self.assertFalse(email_service.smtp_use_tls)
        self.assertEqual(email_service.from_email, "env-noreply@voxify.com")
        self.assertEqual(email_service.from_name, "Voxify Env")

    def test_get_reset_email_template(self):
        """Test reset email template generation"""
        token = "test-token-123"
        user_name = "John Doe"

        subject, html_content, text_content = self.email_service._get_reset_email_template(token, user_name)

        # Check subject
        self.assertEqual(subject, "Reset Your Voxify Password")

        # Check HTML content contains expected elements
        self.assertIn("Hello John Doe,", html_content)
        self.assertIn(token, html_content)
        self.assertIn("Reset My Password", html_content)
        self.assertIn("15 minutes", html_content)
        self.assertIn("Voxify", html_content)

        # Check text content contains expected elements
        self.assertIn("Hello John Doe,", text_content)
        self.assertIn(token, text_content)
        self.assertIn("15 minutes", text_content)

    def test_get_reset_email_template_no_name(self):
        """Test reset email template generation without user name"""
        token = "test-token-456"

        subject, html_content, text_content = self.email_service._get_reset_email_template(token)

        # Check generic greeting is used
        self.assertIn("Hello,", html_content)
        self.assertIn("Hello,", text_content)
        self.assertNotIn("Hello None,", html_content)

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Test email sending
        success, error_msg = self.email_service._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text",
        )

        # Verify success
        self.assertTrue(success)
        self.assertEqual(error_msg, "")

        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "testpass")
        mock_server.send_message.assert_called_once()

    def test_send_email_incomplete_config(self):
        """Test email sending with incomplete configuration"""
        # Create service with incomplete config
        incomplete_config = {"host": "smtp.test.com"}
        email_service = EmailService(incomplete_config)

        success, error_msg = email_service._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
        )

        self.assertFalse(success)
        self.assertEqual(error_msg, "SMTP configuration is incomplete")

    @patch("smtplib.SMTP")
    def test_send_password_reset_email_success(self, mock_smtp):
        """Test successful password reset email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Test password reset email sending
        success, error_msg = self.email_service.send_password_reset_email(
            to_email="test@example.com",
            reset_token="test-token-123",
            user_name="John Doe",
        )

        # Verify success
        self.assertTrue(success)
        self.assertEqual(error_msg, "")

        # Verify SMTP was called
        mock_smtp.assert_called_once()

    @patch("smtplib.SMTP")
    def test_test_connection_success(self, mock_smtp):
        """Test successful SMTP connection test"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        success, message = self.email_service.test_connection()

        self.assertTrue(success)
        self.assertEqual(message, "SMTP connection successful")

        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "testpass")

    def test_test_connection_incomplete_config(self):
        """Test connection test with incomplete configuration"""
        incomplete_config = {"host": "smtp.test.com"}
        email_service = EmailService(incomplete_config)

        success, message = email_service.test_connection()

        self.assertFalse(success)
        self.assertEqual(message, "SMTP configuration is incomplete")


if __name__ == "__main__":
    unittest.main()
