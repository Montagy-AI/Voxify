"""
Job Management API Integration Tests
Complete integration tests for job management with proper JWT authentication and database handling
"""

import pytest
import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from api.v1.job.routes import job_bp
from database.models import (
    get_database_manager,
    User,
    SynthesisJob,
    VoiceModel,
    VoiceSample,
)


@pytest.fixture(scope="session")
def setup_database():
    """Initialize database tables for all tests"""
    import os

    # Use a test-specific database path
    test_db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "test_voxify.db")
    test_db_url = f"sqlite:///{test_db_path}"

    # Set environment variable for this test session
    os.environ["DATABASE_URL"] = test_db_url

    db_manager = get_database_manager(test_db_url)

    # Force recreate tables
    db_manager.drop_tables()
    db_manager.create_tables()
    db_manager.init_default_data()

    return db_manager


@pytest.fixture
def app(setup_database):
    """Create and configure a Flask app for testing"""
    app = Flask(__name__)

    # Configure JWT
    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    JWTManager(app)

    # Register blueprint
    app.register_blueprint(job_bp, url_prefix="/api/v1/job")

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
def cleanup_test_data():
    """Cleanup fixture to remove test data from database"""
    # Clean up before test
    try:
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Delete test users and related data
        test_emails = [
            "job_create_test@example.com",
            "job_list_test@example.com",
            "job_update_test@example.com",
            "job_delete_test@example.com",
            "job_progress_test@example.com",
            "job_validation_test@example.com",
            "job_access_control_user1@example.com",
            "job_access_control_user2@example.com",
        ]

        for email in test_emails:
            user = session.query(User).filter_by(email=email).first()
            if user:
                # Delete related synthesis jobs
                jobs = session.query(SynthesisJob).filter_by(user_id=user.id).all()
                for job in jobs:
                    session.delete(job)

                # Delete related voice models
                voice_samples = session.query(VoiceSample).filter_by(user_id=user.id).all()
                for sample in voice_samples:
                    models = session.query(VoiceModel).filter_by(voice_sample_id=sample.id).all()
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
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Delete test users and related data
        test_emails = [
            "job_create_test@example.com",
            "job_list_test@example.com",
            "job_update_test@example.com",
            "job_delete_test@example.com",
            "job_progress_test@example.com",
            "job_validation_test@example.com",
            "job_access_control_user1@example.com",
            "job_access_control_user2@example.com",
        ]

        for email in test_emails:
            user = session.query(User).filter_by(email=email).first()
            if user:
                # Delete related synthesis jobs
                jobs = session.query(SynthesisJob).filter_by(user_id=user.id).all()
                for job in jobs:
                    session.delete(job)

                # Delete related voice models
                voice_samples = session.query(VoiceSample).filter_by(user_id=user.id).all()
                for sample in voice_samples:
                    models = session.query(VoiceModel).filter_by(voice_sample_id=sample.id).all()
                    for model in models:
                        session.delete(model)
                    session.delete(sample)

                session.delete(user)

        session.commit()
        session.close()
    except Exception:
        pass  # Ignore cleanup errors


class TestJobIntegration:
    """Integration tests for job management"""

    def test_complete_job_lifecycle(self, client, temp_file_storage, cleanup_test_data):
        """Test complete job lifecycle: create -> list -> get -> update -> progress -> delete"""

        # Create test data
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Create user
        user = User(
            email="job_create_test@example.com",
            password_hash="hashed_password",
            first_name="Job",
            last_name="Test",
        )
        session.add(user)
        session.commit()

        # Create voice sample
        voice_sample = VoiceSample(
            user_id=user.id,
            name="Test Voice Sample",
            description="Test voice sample for job testing",
            file_path="/test/path/sample.wav",
            file_size=1024,
            format="wav",
            duration=5.0,
            sample_rate=22050,
            status="ready",
        )
        session.add(voice_sample)
        session.commit()

        # Create voice model
        voice_model = VoiceModel(
            voice_sample_id=voice_sample.id,
            name="Test Voice Model",
            description="Test voice model for job testing",
            model_path="/test/path/model.pth",
            status="completed",
            is_active=True,
        )
        session.add(voice_model)
        session.commit()

        # Create access token within app context
        with client.application.app_context():
            access_token = create_access_token(identity=user.id)

        # Test job creation
        job_data = {
            "text_content": "Hello world, this is a test synthesis job.",
            "voice_model_id": voice_model.id,
            "text_language": "en-US",
            "output_format": "wav",
            "sample_rate": 22050,
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 1.0,
            "config": {"include_timestamps": True, "timestamp_granularity": "word"},
        }

        response = client.post(
            "/api/v1/job",
            json=job_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code in (200, 201)
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        job_id = data["data"]["id"]

        # Test job listing
        response = client.get(
            "/api/v1/job",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

        # Test job details
        response = client.get(
            f"/api/v1/job/{job_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["id"] == job_id

        # Test job update
        update_data = {
            "text_content": "Updated text content for testing.",
            "speed": 1.2,
            "pitch": 0.9,
        }

        response = client.put(
            f"/api/v1/job/{job_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["text_content"] == update_data["text_content"]

        # Test job progress update
        progress_data = {
            "status": "processing",
            "progress": 0.5,
            "processing_node": "test-worker-1",
        }

        response = client.patch(
            f"/api/v1/job/{job_id}",
            json=progress_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["status"] == progress_data["status"]
        assert data["data"]["progress"] == progress_data["progress"]

        # Test job completion
        completion_data = {
            "status": "completed",
            "progress": 1.0,
            "output_path": temp_file_storage["test_file_path"],
            "output_size": 1024,
            "duration": 3.5,
            "processing_time_ms": 2500,
        }

        response = client.patch(
            f"/api/v1/job/{job_id}",
            json=completion_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["status"] == "completed"
        assert data["data"]["progress"] == 1.0

        # Test job deletion
        response = client.delete(
            f"/api/v1/job/{job_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code in (200, 204)
        if response.status_code == 200:
            data = response.get_json()
            assert data["success"] is True
        # For 204 No Content, no JSON response is expected

        # Verify job is deleted
        response = client.get(
            f"/api/v1/job/{job_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

        session.close()

    def test_job_creation_validation(self, client, temp_file_storage, cleanup_test_data):
        """Test job creation with various validation scenarios"""

        # Create test data
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Create user
        user = User(
            email="job_validation_test@example.com",
            password_hash="hashed_password",
            first_name="Validation",
            last_name="Test",
        )
        session.add(user)
        session.commit()

        # Create voice sample and model
        voice_sample = VoiceSample(
            user_id=user.id,
            name="Test Voice Sample",
            description="Test voice sample for validation",
            file_path="/test/path/sample.wav",
            file_size=1024,
            format="wav",
            duration=5.0,
            sample_rate=22050,
            status="ready",
        )
        session.add(voice_sample)
        session.commit()

        voice_model = VoiceModel(
            voice_sample_id=voice_sample.id,
            name="Test Voice Model",
            description="Test voice model for validation",
            model_path="/test/path/model.pth",
            status="completed",
            is_active=True,
        )
        session.add(voice_model)
        session.commit()

        # Create access token within app context
        with client.application.app_context():
            access_token = create_access_token(identity=user.id)

        # Test missing required fields
        invalid_data = {
            "text_content": "Test content"
            # Missing voice_model_id
        }

        response = client.post(
            "/api/v1/job",
            json=invalid_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "voice_model_id" in data["error"]["details"]

        # Test invalid speed value
        invalid_speed_data = {
            "text_content": "Test content",
            "voice_model_id": voice_model.id,
            "speed": 5.0,  # Invalid speed
        }

        response = client.post(
            "/api/v1/job",
            json=invalid_speed_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "speed" in data["error"]["details"]

        # Test invalid output format
        invalid_format_data = {
            "text_content": "Test content",
            "voice_model_id": voice_model.id,
            "output_format": "invalid_format",
        }

        response = client.post(
            "/api/v1/job",
            json=invalid_format_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "output_format" in data["error"]["details"]

        # Test invalid sample rate
        invalid_sample_rate_data = {
            "text_content": "Test content",
            "voice_model_id": voice_model.id,
            "sample_rate": 12345,  # Invalid sample rate
        }

        response = client.post(
            "/api/v1/job",
            json=invalid_sample_rate_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "sample_rate" in data["error"]["details"]

        session.close()

    def test_job_listing_with_filters(self, client, temp_file_storage, cleanup_test_data):
        """Test job listing with various filters and pagination"""

        # Create test data
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Create user
        user = User(
            email="job_list_test@example.com",
            password_hash="hashed_password",
            first_name="List",
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
            name="Test Voice Model",
            description="Test voice model for listing",
            model_path="/test/path/model.pth",
            status="completed",
            is_active=True,
        )
        session.add(voice_model)
        session.commit()

        # Create multiple jobs with different statuses
        jobs_data = [
            {"text_content": "Job 1 - Pending", "status": "pending", "progress": 0.0},
            {
                "text_content": "Job 2 - Processing",
                "status": "processing",
                "progress": 0.5,
            },
            {
                "text_content": "Job 3 - Completed",
                "status": "completed",
                "progress": 1.0,
                "output_path": temp_file_storage["test_file_path"],
                "duration": 2.0,
            },
        ]

        for job_data in jobs_data:
            job = SynthesisJob(
                user_id=user.id,
                voice_model_id=voice_model.id,
                text_content=job_data["text_content"],
                text_hash="test_hash",
                text_language="en-US",
                status=job_data["status"],
                progress=job_data["progress"],
                output_path=job_data.get("output_path"),
                duration=job_data.get("duration"),
            )
            session.add(job)

        session.commit()

        # Create access token within app context
        with client.application.app_context():
            access_token = create_access_token(identity=user.id)

        # Test listing all jobs
        response = client.get("/api/v1/job", headers={"Authorization": f"Bearer {access_token}"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) >= 3

        # Test filtering by status
        response = client.get(
            "/api/v1/job?status=pending",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        for job in data["data"]:
            assert job["status"] == "pending"

        # Test filtering by voice model
        response = client.get(
            f"/api/v1/job?voice_model_id={voice_model.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        for job in data["data"]:
            assert job["voice_model_id"] == voice_model.id

        # Test text search
        response = client.get(
            "/api/v1/job?text_search=Processing",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) >= 1

        # Test pagination
        response = client.get(
            "/api/v1/job?limit=2&offset=0",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) <= 2
        assert "meta" in data
        assert "pagination" in data["meta"]

    def test_job_access_control(self, client, temp_file_storage, cleanup_test_data):
        """Test job access control between different users"""

        # Create test data
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Create two users
        user1 = User(
            email="job_access_control_user1@example.com",
            password_hash="hashed_password",
            first_name="User1",
            last_name="Test",
        )
        session.add(user1)
        session.commit()

        user2 = User(
            email="job_access_control_user2@example.com",
            password_hash="hashed_password",
            first_name="User2",
            last_name="Test",
        )
        session.add(user2)
        session.commit()

        # Create voice sample and model for user1
        voice_sample = VoiceSample(
            user_id=user1.id,
            name="Test Voice Sample",
            description="Test voice sample for access control",
            file_path="/test/path/sample.wav",
            file_size=1024,
            format="wav",
            duration=5.0,
            sample_rate=22050,
            status="ready",
        )
        session.add(voice_sample)
        session.commit()

        voice_model = VoiceModel(
            voice_sample_id=voice_sample.id,
            name="Test Voice Model",
            description="Test voice model for access control",
            model_path="/test/path/model.pth",
            status="completed",
            is_active=True,
        )
        session.add(voice_model)
        session.commit()

        # Create job for user1
        job = SynthesisJob(
            user_id=user1.id,
            voice_model_id=voice_model.id,
            text_content="Test content for access control",
            text_hash="access_hash",
            text_language="en-US",
            status="completed",
        )
        session.add(job)
        session.commit()

        # Get user IDs and job ID before closing session
        user1_id = user1.id
        user2_id = user2.id
        job_id = job.id
        session.close()

        # Create JWT tokens within app context
        with client.application.app_context():
            user1_token = create_access_token(identity=user1_id)
            user2_token = create_access_token(identity=user2_id)

        # Test that user1 can access their own job
        response = client.get(f"/api/v1/job/{job_id}", headers={"Authorization": f"Bearer {user1_token}"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["id"] == job_id

        # Test that user2 cannot access user1's job
        response = client.get(f"/api/v1/job/{job_id}", headers={"Authorization": f"Bearer {user2_token}"})

        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
        assert data["error"]["code"] == "ACCESS_DENIED"

        # Test that user2 cannot update user1's job
        update_data = {"speed": 1.2}
        response = client.put(
            f"/api/v1/job/{job_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {user2_token}"},
        )

        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
        assert data["error"]["code"] == "ACCESS_DENIED"

    def test_job_status_transitions(self, client, temp_file_storage, cleanup_test_data):
        """Test job status transitions and validation"""

        # Create test data
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Create user
        user = User(
            email="job_update_test@example.com",
            password_hash="hashed_password",
            first_name="Update",
            last_name="Test",
        )
        session.add(user)
        session.commit()

        # Create voice sample and model
        voice_sample = VoiceSample(
            user_id=user.id,
            name="Test Voice Sample",
            description="Test voice sample for status transitions",
            file_path="/test/path/sample.wav",
            file_size=1024,
            format="wav",
            duration=5.0,
            sample_rate=22050,
            status="ready",
        )
        session.add(voice_sample)
        session.commit()

        voice_model = VoiceModel(
            voice_sample_id=voice_sample.id,
            name="Test Voice Model",
            description="Test voice model for status transitions",
            model_path="/test/path/model.pth",
            status="completed",
            is_active=True,
        )
        session.add(voice_model)
        session.commit()

        # Create job
        job = SynthesisJob(
            user_id=user.id,
            voice_model_id=voice_model.id,
            text_content="Test content for status transitions",
            text_hash="status_hash",
            text_language="en-US",
            status="pending",
        )
        session.add(job)
        session.commit()

        # Get user ID and job ID before closing session
        user_id = user.id
        job_id = job.id
        session.close()

        # Create JWT token within app context
        with client.application.app_context():
            access_token = create_access_token(identity=user_id)

        # Test valid status transition: pending -> processing
        patch_data = {"status": "processing"}
        response = client.patch(
            f"/api/v1/job/{job_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "processing"

        # Test valid status transition: processing -> completed
        patch_data = {
            "status": "completed",
            "progress": 1.0,
            "output_path": temp_file_storage["test_file_path"],
            "duration": 2.0,
        }
        response = client.patch(
            f"/api/v1/job/{job_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "completed"

        # Test invalid status transition: completed -> processing
        patch_data = {"status": "processing"}
        response = client.patch(
            f"/api/v1/job/{job_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "status" in data["error"]["message"]

    def test_job_deletion_rules(self, client, temp_file_storage, cleanup_test_data):
        """Test job deletion rules and restrictions"""

        # Create test data
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Create user
        user = User(
            email="job_delete_test@example.com",
            password_hash="hashed_password",
            first_name="Delete",
            last_name="Test",
        )
        session.add(user)
        session.commit()

        # Create voice sample and model
        voice_sample = VoiceSample(
            user_id=user.id,
            name="Test Voice Sample",
            description="Test voice sample for deletion rules",
            file_path="/test/path/sample.wav",
            file_size=1024,
            format="wav",
            duration=5.0,
            sample_rate=22050,
            status="ready",
        )
        session.add(voice_sample)
        session.commit()

        voice_model = VoiceModel(
            voice_sample_id=voice_sample.id,
            name="Test Voice Model",
            description="Test voice model for deletion rules",
            model_path="/test/path/model.pth",
            status="completed",
            is_active=True,
        )
        session.add(voice_model)
        session.commit()

        # Create jobs with different statuses
        pending_job = SynthesisJob(
            user_id=user.id,
            voice_model_id=voice_model.id,
            text_content="Pending job",
            text_hash="pending_hash",
            text_language="en-US",
            status="pending",
        )
        session.add(pending_job)

        processing_job = SynthesisJob(
            user_id=user.id,
            voice_model_id=voice_model.id,
            text_content="Processing job",
            text_hash="processing_hash",
            text_language="en-US",
            status="processing",
        )
        session.add(processing_job)

        completed_job = SynthesisJob(
            user_id=user.id,
            voice_model_id=voice_model.id,
            text_content="Completed job",
            text_hash="completed_hash",
            text_language="en-US",
            status="completed",
            output_path=temp_file_storage["test_file_path"],
            duration=2.0,
        )
        session.add(completed_job)

        session.commit()

        # Get user ID and job IDs before closing session
        user_id = user.id
        pending_job_id = pending_job.id
        processing_job_id = processing_job.id
        completed_job_id = completed_job.id
        session.close()

        # Create JWT token within app context
        with client.application.app_context():
            access_token = create_access_token(identity=user_id)

        # Test that pending jobs cannot be deleted
        response = client.delete(
            f"/api/v1/job/{pending_job_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "pending" in data["error"]["message"]

        # Test that processing jobs cannot be deleted
        response = client.delete(
            f"/api/v1/job/{processing_job_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "processing" in data["error"]["message"]

        # Test that completed jobs can be deleted
        response = client.delete(
            f"/api/v1/job/{completed_job_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 204

    def test_job_progress_streaming(self, client, temp_file_storage, cleanup_test_data):
        """Test job progress streaming functionality"""

        # Create test data
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Create user
        user = User(
            email="job_progress_test@example.com",
            password_hash="hashed_password",
            first_name="Progress",
            last_name="Test",
        )
        session.add(user)
        session.commit()

        # Create voice sample and model
        voice_sample = VoiceSample(
            user_id=user.id,
            name="Test Voice Sample",
            description="Test voice sample for progress streaming",
            file_path="/test/path/sample.wav",
            file_size=1024,
            format="wav",
            duration=5.0,
            sample_rate=22050,
            status="ready",
        )
        session.add(voice_sample)
        session.commit()

        voice_model = VoiceModel(
            voice_sample_id=voice_sample.id,
            name="Test Voice Model",
            description="Test voice model for progress streaming",
            model_path="/test/path/model.pth",
            status="completed",
            is_active=True,
        )
        session.add(voice_model)
        session.commit()

        # Create job
        job = SynthesisJob(
            user_id=user.id,
            voice_model_id=voice_model.id,
            text_content="Test content for progress streaming",
            text_hash="progress_hash",
            text_language="en-US",
            status="processing",
            progress=0.3,
        )
        session.add(job)
        session.commit()

        # Get user ID and job ID before closing session
        user_id = user.id
        job_id = job.id
        session.close()

        # Create JWT token within app context
        with client.application.app_context():
            access_token = create_access_token(identity=user_id)

        # Test progress streaming endpoint
        response = client.get(
            f"/api/v1/job/{job_id}/progress",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["Content-Type"]

        # Test that non-existent job returns 404
        response = client.get(
            "/api/v1/job/non-existent-job/progress",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert data["error"]["code"] == "JOB_NOT_FOUND"

    def test_job_duplicate_detection(self, client, temp_file_storage, cleanup_test_data):
        """Test job duplicate detection based on text hash and configuration"""

        # Create test data
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Create user
        user = User(
            email="job_create_test@example.com",
            password_hash="hashed_password",
            first_name="Duplicate",
            last_name="Test",
        )
        session.add(user)
        session.commit()

        # Create voice sample and model
        voice_sample = VoiceSample(
            user_id=user.id,
            name="Test Voice Sample",
            description="Test voice sample for duplicate detection",
            file_path="/test/path/sample.wav",
            file_size=1024,
            format="wav",
            duration=5.0,
            sample_rate=22050,
            status="ready",
        )
        session.add(voice_sample)
        session.commit()

        voice_model = VoiceModel(
            voice_sample_id=voice_sample.id,
            name="Test Voice Model",
            description="Test voice model for duplicate detection",
            model_path="/test/path/model.pth",
            status="completed",
            is_active=True,
        )
        session.add(voice_model)
        session.commit()

        # Get user ID and voice model ID before closing session
        user_id = user.id
        voice_model_id = voice_model.id
        session.close()

        # Create JWT token within app context
        with client.application.app_context():
            access_token = create_access_token(identity=user_id)

        # Create first job
        job_data = {
            "text_content": "This is a duplicate test job.",
            "voice_model_id": voice_model_id,
            "output_format": "wav",
            "sample_rate": 22050,
        }

        first_response = client.post(
            "/api/v1/job",
            json=job_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert first_response.status_code == 201
        first_data = first_response.get_json()
        assert first_data["success"] is True

        # Create duplicate job with same text and configuration
        second_response = client.post(
            "/api/v1/job",
            json=job_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert second_response.status_code == 200  # Returns existing job
        second_data = second_response.get_json()
        assert second_data["success"] is True
        assert "Duplicate synthesis job already exists" in second_data["message"]
        assert second_data["data"]["id"] == first_data["data"]["id"]

        # Create job with same text but different configuration
        different_config_data = {
            "text_content": "This is a duplicate test job.",
            "voice_model_id": voice_model_id,
            "output_format": "mp3",  # Different format
            "sample_rate": 44100,  # Different sample rate
        }

        different_response = client.post(
            "/api/v1/job",
            json=different_config_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert different_response.status_code == 201  # Creates new job
        different_data = different_response.get_json()
        assert different_data["success"] is True
        assert different_data["data"]["id"] != first_data["data"]["id"]

    def test_job_legacy_cancel_endpoint(self, client, temp_file_storage, cleanup_test_data):
        """Test legacy cancel endpoint functionality"""

        # Create test data
        db_manager = get_database_manager()
        session = db_manager.get_session()

        # Create user
        user = User(
            email="job_update_test@example.com",
            password_hash="hashed_password",
            first_name="Cancel",
            last_name="Test",
        )
        session.add(user)
        session.commit()

        # Create voice sample and model
        voice_sample = VoiceSample(
            user_id=user.id,
            name="Test Voice Sample",
            description="Test voice sample for legacy cancel",
            file_path="/test/path/sample.wav",
            file_size=1024,
            format="wav",
            duration=5.0,
            sample_rate=22050,
            status="ready",
        )
        session.add(voice_sample)
        session.commit()

        voice_model = VoiceModel(
            voice_sample_id=voice_sample.id,
            name="Test Voice Model",
            description="Test voice model for legacy cancel",
            model_path="/test/path/model.pth",
            status="completed",
            is_active=True,
        )
        session.add(voice_model)
        session.commit()

        # Create job
        job = SynthesisJob(
            user_id=user.id,
            voice_model_id=voice_model.id,
            text_content="Test content for legacy cancel",
            text_hash="cancel_hash",
            text_language="en-US",
            status="pending",
        )
        session.add(job)
        session.commit()

        # Get user ID and job ID before closing session
        user_id = user.id
        job_id = job.id
        session.close()

        # Create JWT token within app context
        with client.application.app_context():
            access_token = create_access_token(identity=user_id)

        # Test legacy cancel endpoint
        response = client.post(
            f"/api/v1/job/{job_id}/cancel",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "cancelled"
        assert "deprecated" in data["message"]

        # Test that completed jobs cannot be cancelled
        # First update job to completed
        patch_data = {
            "status": "completed",
            "progress": 1.0,
            "output_path": temp_file_storage["test_file_path"],
            "duration": 2.0,
        }
        client.patch(
            f"/api/v1/job/{job_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Try to cancel completed job
        response = client.post(
            f"/api/v1/job/{job_id}/cancel",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "cancelled" in data["error"]["message"]
