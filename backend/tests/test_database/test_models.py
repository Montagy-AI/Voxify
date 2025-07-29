"""
Database Models Unit Tests
Comprehensive test suite for SQLAlchemy ORM models
"""

import pytest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import shutil

# Add the current directory to Python path to find the database module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../.."))

from database.models import (
    Base,
    User,
    VoiceSample,
    VoiceModel,
    SynthesisJob,
    SynthesisCache,
    UsageStat,
    SystemSetting,
    SchemaVersion,
    DatabaseManager,
    get_database_manager,
    generate_uuid,
    TimestampMixin,
)
from sqlalchemy import Column, String


class TestDatabaseUtilities:
    """Test database utility functions"""

    def test_generate_uuid(self):
        """Test UUID generation"""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()

        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)
        assert uuid1 != uuid2
        assert len(uuid1) == 36  # UUID4 format
        assert len(uuid2) == 36

    def test_timestamp_mixin(self):
        """Test TimestampMixin functionality"""

        # Create a mock class with TimestampMixin
        class TestModel(Base, TimestampMixin):
            __tablename__ = "test_model"
            id = Column(String, primary_key=True, default=generate_uuid)

        # Test that the mixin adds timestamp columns
        assert hasattr(TestModel, "created_at")
        assert hasattr(TestModel, "updated_at")


class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self):
        """Test basic user creation"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
        )

        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        # SQLAlchemy default values are only applied when saved to database
        # For testing, we need to check the column default values
        assert User.is_active.default.arg is True
        assert User.email_verified.default.arg is False
        assert User.storage_used_bytes.default.arg == 0

    def test_user_full_name_property(self):
        """Test full_name property"""
        # Test with both names
        user1 = User(first_name="John", last_name="Doe", email="test@example.com")
        assert user1.full_name == "John Doe"

        # Test with only first name
        user2 = User(first_name="John", email="test@example.com")
        assert user2.full_name == "John"

        # Test with only last name
        user3 = User(last_name="Doe", email="test@example.com")
        assert user3.full_name == "Doe"

        # Test with no names
        user4 = User(email="test@example.com")
        assert user4.full_name == "test@example.com"

    def test_user_to_dict(self):
        """Test user serialization to dictionary"""
        user = User(
            id="test-uuid",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            storage_used_bytes=1024,
            is_active=True,
            email_verified=True,
        )

        user_dict = user.to_dict()

        assert user_dict["id"] == "test-uuid"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["first_name"] == "John"
        assert user_dict["last_name"] == "Doe"
        assert user_dict["full_name"] == "John Doe"
        assert user_dict["storage_used_bytes"] == 1024
        assert user_dict["is_active"] is True
        assert user_dict["email_verified"] is True
        assert "created_at" in user_dict
        assert "last_login_at" in user_dict

    def test_user_constraints(self):
        """Test user model constraints"""
        # Test storage_used_bytes constraint
        user = User(email="test@example.com")
        user.storage_used_bytes = -1

        # The constraint should be enforced by SQLAlchemy
        # This test verifies the constraint is defined
        constraints = User.__table_args__
        assert any("storage_used_bytes" in str(constraint) for constraint in constraints)


class TestVoiceSampleModel:
    """Test VoiceSample model functionality"""

    def test_voice_sample_creation(self):
        """Test basic voice sample creation"""
        sample = VoiceSample(
            user_id="user-uuid",
            name="Test Sample",
            description="Test description",
            file_path="/path/to/file.wav",
            file_size=1024,
            format="WAV",
            duration=10.5,
            sample_rate=22050,
        )

        assert sample.user_id == "user-uuid"
        assert sample.name == "Test Sample"
        assert sample.description == "Test description"
        assert sample.file_path == "/path/to/file.wav"
        assert sample.file_size == 1024
        assert sample.format == "WAV"
        assert sample.duration == 10.5
        assert sample.sample_rate == 22050
        # Check column default values
        assert VoiceSample.status.default.arg == "uploaded"

    def test_voice_sample_tags_property(self):
        """Test tags property getter and setter"""
        sample = VoiceSample(user_id="user-uuid", name="Test")

        # Test setting tags
        sample.tags_list = ["tag1", "tag2", "tag3"]
        assert sample.tags == '["tag1", "tag2", "tag3"]'

        # Test getting tags
        sample.tags = '["tag4", "tag5"]'
        assert sample.tags_list == ["tag4", "tag5"]

        # Test empty tags
        sample.tags_list = []
        assert sample.tags == "[]"

        # Test None tags
        sample.tags = None
        assert sample.tags_list == []

    def test_voice_sample_to_dict(self):
        """Test voice sample serialization"""
        sample = VoiceSample(
            id="sample-uuid",
            user_id="user-uuid",
            name="Test Sample",
            description="Test description",
            file_path="/path/to/file.wav",
            file_size=1024,
            format="WAV",
            duration=10.5,
            sample_rate=22050,
            quality_score=8.5,
            language="en-US",
        )

        sample_dict = sample.to_dict()

        assert sample_dict["id"] == "sample-uuid"
        assert sample_dict["user_id"] == "user-uuid"
        assert sample_dict["name"] == "Test Sample"
        assert sample_dict["description"] == "Test description"
        assert sample_dict["file_path"] == "/path/to/file.wav"
        assert sample_dict["file_size"] == 1024
        assert sample_dict["format"] == "WAV"
        assert sample_dict["duration"] == 10.5
        assert sample_dict["sample_rate"] == 22050
        assert sample_dict["quality_score"] == 8.5
        assert sample_dict["language"] == "en-US"
        assert "created_at" in sample_dict
        assert "updated_at" in sample_dict


class TestVoiceModelModel:
    """Test VoiceModel model functionality"""

    def test_voice_model_creation(self):
        """Test basic voice model creation"""
        model = VoiceModel(
            voice_sample_id="sample-uuid",
            name="Test Model",
            description="Test model description",
            model_path="/path/to/model.pth",
            model_type="tacotron2",
            status="completed",
        )

        assert model.voice_sample_id == "sample-uuid"
        assert model.name == "Test Model"
        assert model.description == "Test model description"
        assert model.model_path == "/path/to/model.pth"
        assert model.model_type == "tacotron2"
        assert model.status == "completed"
        # Check column default values
        assert VoiceModel.is_active.default.arg is True



    def test_voice_model_to_dict(self):
        """Test voice model serialization"""
        model = VoiceModel(
            id="model-uuid",
            voice_sample_id="sample-uuid",
            name="Test Model",
            description="Test description",
            model_path="/path/to/model.pth",
            model_type="tacotron2",
            model_size=1024000,
            status="completed",
        )

        model_dict = model.to_dict()

        assert model_dict["id"] == "model-uuid"
        assert model_dict["voice_sample_id"] == "sample-uuid"
        assert model_dict["name"] == "Test Model"
        assert model_dict["description"] == "Test description"
        # model_path is not included in to_dict() method
        assert model_dict["model_type"] == "tacotron2"
        assert model_dict["model_size"] == 1024000
        assert model_dict["status"] == "completed"
        assert "created_at" in model_dict
        assert "updated_at" in model_dict


class TestSynthesisJobModel:
    """Test SynthesisJob model functionality"""

    def test_synthesis_job_creation(self):
        """Test basic synthesis job creation"""
        job = SynthesisJob(
            user_id="user-uuid",
            voice_model_id="model-uuid",
            text_content="Hello world",
            text_hash="hash123",
            status="pending",
        )

        assert job.user_id == "user-uuid"
        assert job.voice_model_id == "model-uuid"
        assert job.text_content == "Hello world"
        assert job.text_hash == "hash123"
        assert job.status == "pending"
        # Check column default values
        assert SynthesisJob.progress.default.arg == 0.0

    def test_synthesis_job_config_property(self):
        """Test config property getter and setter"""
        job = SynthesisJob(user_id="user-uuid", voice_model_id="model-uuid", text_content="test")

        # Test setting config
        config = {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
        job.config_dict = config
        assert job.config == '{"speed": 1.0, "pitch": 1.0, "volume": 1.0}'

        # Test getting config
        job.config = '{"speed": 1.2, "pitch": 0.8}'
        assert job.config_dict == {"speed": 1.2, "pitch": 0.8}



    def test_synthesis_job_to_dict(self):
        """Test synthesis job serialization"""
        job = SynthesisJob(
            id="job-uuid",
            user_id="user-uuid",
            voice_model_id="model-uuid",
            text_content="Hello world",
            text_hash="hash123",
            status="completed",
            progress=100.0,
            output_path="/path/to/output.wav",
            duration=2.5,
        )

        job_dict = job.to_dict()

        assert job_dict["id"] == "job-uuid"
        assert job_dict["user_id"] == "user-uuid"
        assert job_dict["voice_model_id"] == "model-uuid"
        assert job_dict["text_content"] == "Hello world"
        assert job_dict["text_hash"] == "hash123"
        assert job_dict["status"] == "completed"
        assert job_dict["progress"] == 100.0
        assert job_dict["output_path"] == "/path/to/output.wav"
        assert job_dict["duration"] == 2.5
        assert "created_at" in job_dict
        # Note: updated_at is not included in to_dict() method


class TestSynthesisCacheModel:
    """Test SynthesisCache model functionality"""

    def test_synthesis_cache_creation(self):
        """Test basic synthesis cache creation"""
        cache = SynthesisCache(
            text_hash="hash123",
            voice_model_id="model-uuid",
            config_hash="config_hash",
            output_path="/path/to/cached.wav",
            duration=2.5,
        )

        assert cache.text_hash == "hash123"
        assert cache.voice_model_id == "model-uuid"
        assert cache.config_hash == "config_hash"
        assert cache.output_path == "/path/to/cached.wav"
        assert cache.duration == 2.5
        # Check column default values
        assert SynthesisCache.hit_count.default.arg == 0





class TestUsageStatModel:
    """Test UsageStat model functionality"""

    def test_usage_stat_creation(self):
        """Test basic usage stat creation"""
        stat = UsageStat(
            user_id="user-uuid",
            date="2024-01-01",
            voice_samples_uploaded=5,
            synthesis_requests=10,
            synthesis_duration=30.5,
        )

        assert stat.user_id == "user-uuid"
        assert stat.date == "2024-01-01"
        assert stat.voice_samples_uploaded == 5
        assert stat.synthesis_requests == 10
        assert stat.synthesis_duration == 30.5


class TestSystemSettingModel:
    """Test SystemSetting model functionality"""

    def test_system_setting_creation(self):
        """Test basic system setting creation"""
        setting = SystemSetting(
            key="max_file_size",
            value="10485760",
            data_type="integer",
            description="Maximum file size in bytes",
        )

        assert setting.key == "max_file_size"
        assert setting.value == "10485760"
        assert setting.data_type == "integer"
        assert setting.description == "Maximum file size in bytes"
        # Check column default values
        assert SystemSetting.is_public.default.arg is False

    def test_system_setting_get_typed_value(self):
        """Test get_typed_value method"""
        # Test integer
        setting_int = SystemSetting(key="test_int", value="123", data_type="integer")
        assert setting_int.get_typed_value() == 123

        # Test float
        setting_float = SystemSetting(key="test_float", value="123.45", data_type="float")
        assert setting_float.get_typed_value() == 123.45

        # Test boolean
        setting_bool = SystemSetting(key="test_bool", value="true", data_type="boolean")
        assert setting_bool.get_typed_value() is True

        # Test string
        setting_string = SystemSetting(key="test_string", value="hello", data_type="string")
        assert setting_string.get_typed_value() == "hello"

        # Test unknown type
        setting_unknown = SystemSetting(key="test_unknown", value="test", data_type="unknown")
        assert setting_unknown.get_typed_value() == "test"


class TestSchemaVersionModel:
    """Test SchemaVersion model functionality"""

    def test_schema_version_creation(self):
        """Test basic schema version creation"""
        version = SchemaVersion(version="1.0.0", description="Initial schema version")

        assert version.version == "1.0.0"
        assert version.description == "Initial schema version"


class TestDatabaseManager:
    """Test DatabaseManager functionality"""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        yield db_path
        # Close any open connections before cleanup
        try:
            import time

            time.sleep(0.1)  # Give time for connections to close
            shutil.rmtree(temp_dir)
        except PermissionError:
            # On Windows, sometimes files are still in use
            pass

    def test_database_manager_creation(self, temp_db_path):
        """Test database manager creation"""
        db_url = f"sqlite:///{temp_db_path}"
        manager = DatabaseManager(db_url)

        # DatabaseManager doesn't store database_url as an attribute
        assert manager.engine is not None
        assert manager.SessionLocal is not None

    def test_create_tables(self, temp_db_path):
        """Test table creation"""
        db_url = f"sqlite:///{temp_db_path}"
        manager = DatabaseManager(db_url)

        # Create tables
        manager.create_tables()

        # Verify tables exist by checking if we can create a session
        session = manager.get_session()
        assert session is not None
        session.close()

    def test_drop_tables(self, temp_db_path):
        """Test table dropping"""
        db_url = f"sqlite:///{temp_db_path}"
        manager = DatabaseManager(db_url)

        # Create tables first
        manager.create_tables()

        # Drop tables
        manager.drop_tables()

        # Verify tables are dropped by checking if we can still create a session
        # (this should work even with no tables)
        session = manager.get_session()
        assert session is not None
        session.close()

    def test_get_session(self, temp_db_path):
        """Test session creation"""
        db_url = f"sqlite:///{temp_db_path}"
        manager = DatabaseManager(db_url)

        session = manager.get_session()
        assert session is not None
        session.close()

    def test_init_default_data(self, temp_db_path):
        """Test default data initialization"""
        db_url = f"sqlite:///{temp_db_path}"
        manager = DatabaseManager(db_url)

        # Create tables and init default data
        manager.create_tables()
        manager.init_default_data()

        # Verify default data was created by checking system settings
        session = manager.get_session()
        try:
            settings = session.query(SystemSetting).all()
            # Should have some default settings
            assert len(settings) > 0
        finally:
            session.close()

    def test_get_database_manager(self, temp_db_path):
        """Test get_database_manager function"""
        db_url = f"sqlite:///{temp_db_path}"
        manager = get_database_manager(db_url)

        assert isinstance(manager, DatabaseManager)
        # DatabaseManager doesn't store database_url as an attribute
        assert manager.engine is not None


class TestDatabaseRelationships:
    """Test database relationships and cascading"""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        yield db_path
        # Close any open connections before cleanup
        try:
            import time

            time.sleep(0.1)  # Give time for connections to close
            shutil.rmtree(temp_dir)
        except PermissionError:
            # On Windows, sometimes files are still in use
            pass

    def test_user_voice_samples_relationship(self, temp_db_path):
        """Test user-voice samples relationship"""
        db_url = f"sqlite:///{temp_db_path}"
        manager = DatabaseManager(db_url)
        manager.create_tables()

        session = manager.get_session()
        try:
            # Create user
            user = User(email="test@example.com", password_hash="hash")
            session.add(user)
            session.commit()

            # Create voice sample
            sample = VoiceSample(
                user_id=user.id,
                name="Test Sample",
                file_path="/path/to/file.wav",
                file_size=1024,
                format="WAV",
                duration=10.0,
                sample_rate=22050,
            )
            session.add(sample)
            session.commit()

            # Test relationship
            assert len(user.voice_samples) == 1
            assert user.voice_samples[0].id == sample.id

            # Test cascade delete
            session.delete(user)
            session.commit()

            # Voice sample should be deleted
            remaining_samples = session.query(VoiceSample).all()
            assert len(remaining_samples) == 0

        finally:
            session.close()

    def test_voice_sample_voice_models_relationship(self, temp_db_path):
        """Test voice sample-voice models relationship"""
        db_url = f"sqlite:///{temp_db_path}"
        manager = DatabaseManager(db_url)
        manager.create_tables()

        session = manager.get_session()
        try:
            # Create user and voice sample
            user = User(email="test@example.com", password_hash="hash")
            session.add(user)
            session.commit()

            sample = VoiceSample(
                user_id=user.id,
                name="Test Sample",
                file_path="/path/to/file.wav",
                file_size=1024,
                format="WAV",
                duration=10.0,
                sample_rate=22050,
            )
            session.add(sample)
            session.commit()

            # Create voice model
            model = VoiceModel(
                voice_sample_id=sample.id,
                name="Test Model",
                model_path="/path/to/model.pth",
                status="completed",
            )
            session.add(model)
            session.commit()

            # Test relationship
            assert len(sample.voice_models) == 1
            assert sample.voice_models[0].id == model.id

            # Test cascade delete
            session.delete(sample)
            session.commit()

            # Voice model should be deleted
            remaining_models = session.query(VoiceModel).all()
            assert len(remaining_models) == 0

        finally:
            session.close()

    def test_synthesis_job_relationships(self, temp_db_path):
        """Test synthesis job relationships"""
        db_url = f"sqlite:///{temp_db_path}"
        manager = DatabaseManager(db_url)
        manager.create_tables()

        session = manager.get_session()
        try:
            # Create user, voice sample, and voice model
            user = User(email="test@example.com", password_hash="hash")
            session.add(user)
            session.commit()

            sample = VoiceSample(
                user_id=user.id,
                name="Test Sample",
                file_path="/path/to/file.wav",
                file_size=1024,
                format="WAV",
                duration=10.0,
                sample_rate=22050,
            )
            session.add(sample)
            session.commit()

            model = VoiceModel(
                voice_sample_id=sample.id,
                name="Test Model",
                model_path="/path/to/model.pth",
                status="completed",
            )
            session.add(model)
            session.commit()

            # Create synthesis job
            job = SynthesisJob(
                user_id=user.id,
                voice_model_id=model.id,
                text_content="Hello world",
                text_hash="hash123",
            )
            session.add(job)
            session.commit()

            # Test relationships
            assert len(user.synthesis_jobs) == 1
            assert user.synthesis_jobs[0].id == job.id

            assert len(model.synthesis_jobs) == 1
            assert model.synthesis_jobs[0].id == job.id

            # Test cascade delete
            session.delete(user)
            session.commit()

            # Job should be deleted
            remaining_jobs = session.query(SynthesisJob).all()
            assert len(remaining_jobs) == 0

        finally:
            session.close()
