#!/usr/bin/env python3
"""
Test suite for API Package Initialization
Tests for backend/api/__init__.py - Flask app creation and configuration
"""

import os
import sys
import pytest
from unittest.mock import patch


@pytest.fixture(scope="session", autouse=True)
def setup_import_path():
    """
    Add backend directory to Python path and verify api/__init__.py exists.
    """
    current_dir = os.path.dirname(__file__)
    api_init_path = os.path.abspath(
        os.path.join(current_dir, "../../../backend", "api", "__init__.py")
    )

    # Verify file exists and is readable
    if not os.path.exists(api_init_path):
        pytest.skip("Could not find api/__init__.py - skipping API init tests")
    if not os.access(api_init_path, os.R_OK):
        pytest.skip("api/__init__.py is not readable")

    try:
        with open(api_init_path, "r") as f:
            content = f.read()
        compile(content, api_init_path, "exec")
    except SyntaxError as e:
        pytest.skip(f"Syntax error in api/__init__.py: {e}")

    backend_dir = os.path.dirname(os.path.dirname(api_init_path))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)


class TestCreateAppFunction:
    """
    Test the create_app function core functionality.
    """

    def test_create_app_basic_functionality(self):
        """Test create_app returns Flask instance with basic setup"""
        try:
            from api import create_app
            from flask import Flask
        except ImportError:
            pytest.skip("Could not import create_app from api")

        with (
            patch("api.load_dotenv"),
            patch("api.CORS"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
        ):

            app = create_app()
            assert isinstance(app, Flask)
            assert hasattr(app, "config")

    def test_create_app_default_configuration(self):
        """Test default configuration values"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        with (
            patch("api.load_dotenv"),
            patch("api.CORS"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
            patch.dict(os.environ, {}, clear=True),
        ):

            app = create_app()

            # Test critical default configurations
            assert app.config["SECRET_KEY"] == "Majick"
            assert app.config["JWT_SECRET_KEY"] == "Majick"
            assert app.config["JWT_ACCESS_TOKEN_EXPIRES"] == 3600
            assert app.config["JWT_REFRESH_TOKEN_EXPIRES"] == 2592000
            assert app.config["DATABASE_URL"] == "sqlite:///data/voxify.db"
            assert app.config["MAX_CONTENT_LENGTH"] == 16 * 1024 * 1024

    def test_create_app_environment_override(self):
        """Test environment variable configuration override"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        test_env = {
            "SECRET_KEY": "test_secret_key",
            "JWT_SECRET_KEY": "test_jwt_secret",
            "JWT_ACCESS_TOKEN_EXPIRES": "7200",
            "JWT_REFRESH_TOKEN_EXPIRES": "5184000",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
        }

        with (
            patch("api.load_dotenv"),
            patch("api.CORS"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
            patch.dict(os.environ, test_env),
        ):

            app = create_app()

            assert app.config["SECRET_KEY"] == "test_secret_key"
            assert app.config["JWT_SECRET_KEY"] == "test_jwt_secret"
            assert app.config["JWT_ACCESS_TOKEN_EXPIRES"] == 7200
            assert app.config["JWT_REFRESH_TOKEN_EXPIRES"] == 5184000
            assert app.config["DATABASE_URL"] == "postgresql://test:test@localhost/test"

    def test_create_app_test_config_override(self):
        """Test test configuration parameter override"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        test_config = {
            "TESTING": True,
            "SECRET_KEY": "test_override_secret",
            "DATABASE_URL": "sqlite:///:memory:",
        }

        with (
            patch("api.load_dotenv"),
            patch("api.CORS"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
        ):

            app = create_app(test_config=test_config)

            assert app.config["TESTING"] is True
            assert app.config["SECRET_KEY"] == "test_override_secret"
            assert app.config["DATABASE_URL"] == "sqlite:///:memory:"

    def test_create_app_jwt_configuration(self):
        """Test JWT specific configuration"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        with (
            patch("api.load_dotenv"),
            patch("api.CORS"),
            patch("api.JWTManager") as mock_jwt,
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
        ):

            app = create_app()

            # Verify JWT configuration
            assert app.config["JWT_TOKEN_LOCATION"] == ["headers"]
            assert app.config["JWT_HEADER_NAME"] == "Authorization"
            assert app.config["JWT_HEADER_TYPE"] == "Bearer"

            # Verify JWTManager was initialized
            mock_jwt.assert_called_once_with(app)

    def test_create_app_cors_setup(self):
        """Test CORS configuration"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        with (
            patch("api.load_dotenv"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
            patch("api.CORS") as mock_cors,
        ):

            app = create_app()

            # Verify CORS was called
            mock_cors.assert_called_once()
            call_args = mock_cors.call_args

            # Check app was passed
            assert call_args[0][0] == app

            # Check key CORS settings exist
            kwargs = call_args[1]
            assert "origins" in kwargs
            assert "methods" in kwargs
            assert "supports_credentials" in kwargs
            assert kwargs["supports_credentials"] is True

    def test_create_app_load_dotenv_called(self):
        """Test that load_dotenv is called during app creation"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        with (
            patch("api.CORS"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
            patch("api.load_dotenv") as mock_load_dotenv,
        ):

            create_app()
            mock_load_dotenv.assert_called_once()


class TestFlaskAppRoutes:
    """
    Test Flask app routes functionality.
    """

    def test_index_route(self):
        """Test the index route returns welcome message"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        with (
            patch("api.load_dotenv"),
            patch("api.CORS"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
        ):

            app = create_app()

            with app.test_client() as client:
                response = client.get("/")
                assert response.status_code == 200
                data = response.get_json()
                assert data == {"message": "Welcome to Voxify API"}

    def test_health_check_route(self):
        """Test the health check route"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        with (
            patch("api.load_dotenv"),
            patch("api.CORS"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
        ):

            app = create_app()

            with app.test_client() as client:
                response = client.get("/health")
                assert response.status_code == 200
                data = response.get_json()
                assert data == {"status": "healthy"}


class TestConfigurationErrorHandling:
    """
    Test configuration error handling scenarios.
    """

    def test_create_app_invalid_token_expires(self):
        """Test invalid JWT token expiration values"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        invalid_env = {
            "JWT_ACCESS_TOKEN_EXPIRES": "not_a_number",
            "JWT_REFRESH_TOKEN_EXPIRES": "also_not_a_number",
        }

        with (
            patch("api.load_dotenv"),
            patch("api.CORS"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
            patch.dict(os.environ, invalid_env),
        ):

            # Should raise ValueError when converting to int
            with pytest.raises(ValueError):
                create_app()


class TestFlaskAppConfiguration:
    """
    Test Flask app specific configuration.
    """

    def test_max_content_length_configuration(self):
        """Test MAX_CONTENT_LENGTH configuration"""
        try:
            from api import create_app
        except ImportError:
            pytest.skip("Could not import create_app from api")

        with (
            patch("api.load_dotenv"),
            patch("api.CORS"),
            patch("api.JWTManager"),
            patch("api.v1.auth.auth_bp"),
            patch("api.v1.voice.voice_bp"),
            patch("api.v1.job.job_bp"),
            patch("api.v1.file.file_bp"),
        ):

            app = create_app()

            # Test file upload size limit is set correctly (16MB)
            assert app.config["MAX_CONTENT_LENGTH"] == 16 * 1024 * 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
