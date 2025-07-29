"""
Final File Management API Integration Tests
Complete integration tests for file management with proper JWT authentication and database handling
"""

import pytest
import os
import sys
import tempfile
import shutil
import uuid
from unittest.mock import patch
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, backend_dir)

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from api.v1.file.routes import file_bp
from database.models import (
    get_database_manager,
    User,
    SynthesisJob,
    VoiceModel,
    VoiceSample,
)


@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    app = Flask(__name__)

    # Configure JWT
    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    JWTManager(app)

    # Register blueprint
    app.register_blueprint(file_bp, url_prefix="/api/v1/file")

    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app"""
    return app.test_client()


@pytest.fixture
def temp_file_storage():
    """Create temporary file storage for testing"""
    temp_dir = tempfile.mkdtemp()

    # Create synthesis directories
    synthesis_dir = os.path.join(temp_dir, "synthesis")
    output_dir = os.path.join(synthesis_dir, "output")

    os.makedirs(output_dir, exist_ok=True)

    # Create test audio file
    test_file_path = os.path.join(output_dir, "test_output.wav")
    with open(test_file_path, "wb") as f:
        f.write(
            b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        )

    yield {"temp_dir": temp_dir, "test_file_path": test_file_path}

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_db():
    """Create a test database with in-memory SQLite"""
    # Use in-memory database for testing
    test_db_url = "sqlite:///:memory:"
    db_manager = get_database_manager(test_db_url)

    # Create tables
    db_manager.create_tables()
    db_manager.init_default_data()

    yield db_manager

    # Cleanup is automatic for in-memory database


@pytest.fixture
def cleanup_test_data(test_db):
    """Cleanup fixture to remove test data from database"""
    # Clean up before test
    try:
        session = test_db.get_session()

        # Delete test users and related data
        test_emails = [
            "download_test@example.com",
            "info_test@example.com",
            "delete_test@example.com",
            "access_control_user1@example.com",
            "access_control_user2@example.com",
            "notfound_test_final@example.com",
        ]

        for email in test_emails:
            user = session.query(User).filter_by(email=email).first()
            if user:
                # Delete related synthesis jobs
                jobs = session.query(SynthesisJob).filter_by(user_id=user.id).all()
                for job in jobs:
                    session.delete(job)

                # Delete related voice models
                voice_samples = (
                    session.query(VoiceSample).filter_by(user_id=user.id).all()
                )
                for sample in voice_samples:
                    models = (
                        session.query(VoiceModel)
                        .filter_by(voice_sample_id=sample.id)
                        .all()
                    )
                    for model in models:
                        session.delete(model)
                    session.delete(sample)

                session.delete(user)

        session.commit()
        session.close()
    except Exception:
        pass  # Ignore cleanup errors

    yield  # Run test

    # Clean up after test
    try:
        session = test_db.get_session()

        # Delete test users and related data
        test_emails = [
            "download_test@example.com",
            "info_test@example.com",
            "delete_test@example.com",
            "access_control_user1@example.com",
            "access_control_user2@example.com",
            "notfound_test_final@example.com",
        ]

        for email in test_emails:
            user = session.query(User).filter_by(email=email).first()
            if user:
                # Delete related synthesis jobs
                jobs = session.query(SynthesisJob).filter_by(user_id=user.id).all()
                for job in jobs:
                    session.delete(job)

                # Delete related voice models
                voice_samples = (
                    session.query(VoiceSample).filter_by(user_id=user.id).all()
                )
                for sample in voice_samples:
                    models = (
                        session.query(VoiceModel)
                        .filter_by(voice_sample_id=sample.id)
                        .all()
                    )
                    for model in models:
                        session.delete(model)
                    session.delete(sample)

                session.delete(user)

        session.commit()
        session.close()
    except Exception:
        pass  # Ignore cleanup errors


class TestFileIntegrationFinal:
    """Final integration tests for file management"""

    def test_basic_file_download(
        self, client, temp_file_storage, cleanup_test_data, test_db
    ):
        """Test basic file download with JWT authentication"""

        # Mock the database manager to use test database
        with patch("api.v1.file.routes.get_database_manager", return_value=test_db):
            # Create test data
            session = test_db.get_session()

            # Create user with unique email
            user = User(
                email="download_test@example.com",
                password_hash="hashed_password",
                first_name="Download",
                last_name="Test",
            )
            session.add(user)
            session.commit()

            # Create voice sample
            voice_sample = VoiceSample(
                user_id=user.id,
                name="Test Voice",
                file_path="test_voice.wav",
                file_size=1024,
                format="wav",
                duration=1.0,
                sample_rate=22050,
            )
            session.add(voice_sample)
            session.commit()

            # Create voice model
            voice_model = VoiceModel(
                voice_sample_id=voice_sample.id,
                name="Test Model",
                model_path="test_model.pth",
                status="completed",
            )
            session.add(voice_model)
            session.commit()

            # Create synthesis job
            job = SynthesisJob(
                id="download-job-123",
                user_id=user.id,
                voice_model_id=voice_model.id,
                text_content="Hello, this is a test synthesis.",
                text_hash="download_hash",
                text_language="en-US",
                output_path=temp_file_storage["test_file_path"],
                duration=2.5,
                status="completed",
            )
            session.add(job)
            session.commit()

            # Get user ID before closing session
            user_id = user.id
            session.close()

            # Create JWT token within app context
            with client.application.app_context():
                access_token = create_access_token(identity=user_id)

            # Test download
            response = client.get(
                "/api/v1/file/synthesis/download-job-123",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            assert response.status_code == 200
            assert response.headers["Content-Type"] == "audio/wav"

    def test_file_download_without_auth(self, client):
        """Test file download without authentication"""

        response = client.get("/api/v1/file/synthesis/test-job-123")

        assert response.status_code == 401

    def test_file_info_with_auth(
        self, client, temp_file_storage, cleanup_test_data, test_db
    ):
        """Test file info endpoint with JWT authentication"""

        # Mock the database manager to use test database
        with patch("api.v1.file.routes.get_database_manager", return_value=test_db):
            # Create test data
            session = test_db.get_session()

            # Create user with unique email
            user = User(
                email="info_test@example.com",
                password_hash="hashed_password",
                first_name="Info",
                last_name="Test",
            )
            session.add(user)
            session.commit()

            # Create voice sample and model
            voice_sample = VoiceSample(
                user_id=user.id,
                name="Test Voice",
                file_path="test_voice.wav",
                file_size=1024,
                format="wav",
                duration=1.0,
                sample_rate=22050,
            )
            session.add(voice_sample)
            session.commit()

            voice_model = VoiceModel(
                voice_sample_id=voice_sample.id,
                name="Test Model",
                model_path="test_model.pth",
                status="completed",
            )
            session.add(voice_model)
            session.commit()

            # Create synthesis job
            job = SynthesisJob(
                id="info-job-123",
                user_id=user.id,
                voice_model_id=voice_model.id,
                text_content="Test content for info",
                text_hash="info_hash",
                text_language="en-US",
                output_path=temp_file_storage["test_file_path"],
                status="completed",
            )
            session.add(job)
            session.commit()

            # Get user ID before closing session
            user_id = user.id
            session.close()

            # Create JWT token within app context
            with client.application.app_context():
                access_token = create_access_token(identity=user_id)

            # Test file info
            response = client.get(
                "/api/v1/file/voice-clone/info-job-123/info",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "data" in data
            assert data["data"]["job_id"] == "info-job-123"

    def test_file_delete_with_auth(
        self, client, temp_file_storage, cleanup_test_data, test_db
    ):
        """Test file delete with JWT authentication"""

        # Mock the database manager to use test database
        with patch("api.v1.file.routes.get_database_manager", return_value=test_db):
            # Create test data
            session = test_db.get_session()

            # Create user with unique email
            user = User(
                email="delete_test@example.com",
                password_hash="hashed_password",
                first_name="Delete",
                last_name="Test",
            )
            session.add(user)
            session.commit()

            # Create voice sample and model
            voice_sample = VoiceSample(
                user_id=user.id,
                name="Test Voice",
                file_path="test_voice.wav",
                file_size=1024,
                format="wav",
                duration=1.0,
                sample_rate=22050,
            )
            session.add(voice_sample)
            session.commit()

            voice_model = VoiceModel(
                voice_sample_id=voice_sample.id,
                name="Test Model",
                model_path="test_model.pth",
                status="completed",
            )
            session.add(voice_model)
            session.commit()

            # Create synthesis job
            job = SynthesisJob(
                id="delete-job-123",
                user_id=user.id,
                voice_model_id=voice_model.id,
                text_content="Test content for delete",
                text_hash="delete_hash",
                text_language="en-US",
                output_path=temp_file_storage["test_file_path"],
                status="completed",
            )
            session.add(job)
            session.commit()

            # Get user ID before closing session
            user_id = user.id
            session.close()

            # Create JWT token within app context
            with client.application.app_context():
                access_token = create_access_token(identity=user_id)

            # Test file delete
            response = client.delete(
                "/api/v1/file/synthesis/delete-job-123",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "File deleted successfully" in data["message"]

    def test_access_control(
        self, client, temp_file_storage, cleanup_test_data, test_db
    ):
        """Test file access control between different users"""

        # Mock the database manager to use test database
        with patch("api.v1.file.routes.get_database_manager", return_value=test_db):
            # Create test data
            session = test_db.get_session()

            # Create two users
            user1 = User(
                email="access_control_user1@example.com",
                password_hash="hashed_password",
                first_name="User1",
                last_name="Test",
            )
            session.add(user1)
            session.commit()

            user2 = User(
                email="access_control_user2@example.com",
                password_hash="hashed_password",
                first_name="User2",
                last_name="Test",
            )
            session.add(user2)
            session.commit()

            # Create voice sample and model for user1
            voice_sample = VoiceSample(
                user_id=user1.id,
                name="Test Voice",
                file_path="test_voice.wav",
                file_size=1024,
                format="wav",
                duration=1.0,
                sample_rate=22050,
            )
            session.add(voice_sample)
            session.commit()

            voice_model = VoiceModel(
                voice_sample_id=voice_sample.id,
                name="Test Model",
                model_path="test_model.pth",
                status="completed",
            )
            session.add(voice_model)
            session.commit()

            # Create synthesis job for user1
            job = SynthesisJob(
                id="access-control-job-123",
                user_id=user1.id,
                voice_model_id=voice_model.id,
                text_content="Test content for access control",
                text_hash="access_hash",
                text_language="en-US",
                output_path=temp_file_storage["test_file_path"],
                status="completed",
            )
            session.add(job)
            session.commit()

            # Get user IDs before closing session
            user1_id = user1.id
            user2_id = user2.id
            session.close()

            # Create JWT tokens within app context
            with client.application.app_context():
                user1_token = create_access_token(identity=user1_id)
                user2_token = create_access_token(identity=user2_id)

            # Test that user1 can access their own file
            response = client.get(
                "/api/v1/file/synthesis/access-control-job-123",
                headers={"Authorization": f"Bearer {user1_token}"},
            )

            assert response.status_code == 200

            # Test that user2 cannot access user1's file
            response = client.get(
                "/api/v1/file/synthesis/access-control-job-123",
                headers={"Authorization": f"Bearer {user2_token}"},
            )

            assert response.status_code == 403
            data = response.get_json()
            assert data["success"] is False
            assert data["error"]["code"] == "ACCESS_DENIED"

    def test_file_not_found(
        self, client, temp_file_storage, cleanup_test_data, test_db
    ):
        """Test file not found scenarios"""

        # Mock the database manager to use test database
        with patch("api.v1.file.routes.get_database_manager", return_value=test_db):
            # Create test data
            session = test_db.get_session()

            # Create user
            user = User(
                email="notfound_test_final@example.com",
                password_hash="hashed_password",
                first_name="NotFound",
                last_name="Test",
            )
            session.add(user)
            session.commit()

            # Get user ID before closing session
            user_id = user.id
            session.close()

            # Create JWT token within app context
            with client.application.app_context():
                access_token = create_access_token(identity=user_id)

            # Test non-existent job
            response = client.get(
                "/api/v1/file/synthesis/non-existent-job",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False
            assert data["error"]["code"] == "FILE_NOT_FOUND"
