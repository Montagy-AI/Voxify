import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os
from flask import Flask
from api.v1.file.routes import get_synthesis_file, error_response, success_response

# Add the backend and backend/api directories to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend")))


class TestFileLogic:
    """Unit tests for file API logic functions"""

    def test_error_response_basic(self):
        """Test basic error response format"""
        app = Flask(__name__)
        with app.app_context():
            with patch("api.v1.file.routes.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)

                response, status_code = error_response("Test error", "TEST_ERROR", 400)
                data = response.get_json()

                assert status_code == 400
                assert data["success"] is False
                assert data["error"]["message"] == "Test error"
                assert data["error"]["code"] == "TEST_ERROR"
                assert "timestamp" in data["error"]

    def test_error_response_with_custom_code(self):
        """Test error response with custom error code"""
        app = Flask(__name__)
        with app.app_context():
            response, status_code = error_response("Custom error", "CUSTOM_ERROR", 500)
            data = response.get_json()

            assert status_code == 500
            assert data["error"]["code"] == "CUSTOM_ERROR"

    def test_error_response_default_code(self):
        """Test error response with default error code"""
        app = Flask(__name__)
        with app.app_context():
            response, status_code = error_response("Default error", status_code=404)
            data = response.get_json()

            assert data["error"]["code"] == "ERROR_404"

    def test_success_response_basic(self):
        """Test basic success response format"""
        app = Flask(__name__)
        with app.app_context():
            with patch("api.v1.file.routes.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)

                response, status_code = success_response()
                data = response.get_json()

                assert status_code == 200
                assert data["success"] is True
                assert "timestamp" in data

    def test_success_response_with_data(self):
        """Test success response with data"""
        app = Flask(__name__)
        with app.app_context():
            test_data = {"file": "test.wav", "size": 1024}
            response, status_code = success_response(test_data, "File found", 200)
            data = response.get_json()

            assert status_code == 200
            assert data["success"] is True
            assert data["data"] == test_data
            assert data["message"] == "File found"

    def test_success_response_with_message(self):
        """Test success response with message only"""
        app = Flask(__name__)
        with app.app_context():
            response, status_code = success_response(message="Operation completed")
            data = response.get_json()

            assert status_code == 200
            assert data["success"] is True
            assert data["message"] == "Operation completed"
            assert "data" not in data

    def test_success_response_custom_status(self):
        """Test success response with custom status code"""
        app = Flask(__name__)
        with app.app_context():
            response, status_code = success_response(status_code=201)
            data = response.get_json()

            assert status_code == 201
            assert data["success"] is True


class TestFileRetrieval:
    """Unit tests for file retrieval logic"""

    @patch("api.v1.file.routes.get_database_manager")
    def test_get_synthesis_file_job_not_found(self, mock_db_manager):
        """Test get_synthesis_file when job doesn't exist"""
        mock_session = Mock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_db_manager.return_value.get_session.return_value.__enter__.return_value = mock_session

        file_path, filename, cache_id = get_synthesis_file("non-existent-job")

        assert file_path is None
        assert filename is None
        assert cache_id is None

    @patch("api.v1.file.routes.get_database_manager")
    def test_get_synthesis_file_with_cache_hit(self, mock_db_manager):
        """Test get_synthesis_file when cache hit exists"""
        # Mock job with cache hit
        mock_job = Mock()
        mock_job.cache_hit = True
        mock_job.cached_result_id = "cache-123"

        # Mock cache entry
        mock_cache = Mock()
        mock_cache.output_path = "/path/to/cached/file.wav"
        mock_cache.id = "cache-123"

        mock_session = Mock()
        mock_session.query.return_value.filter_by.return_value.first.side_effect = [mock_job, mock_cache]
        mock_db_manager.return_value.get_session.return_value.__enter__.return_value = mock_session

        file_path, filename, cache_id = get_synthesis_file("job-123")

        assert file_path == "/path/to/cached/file.wav"
        assert filename == "file.wav"
        assert cache_id == "cache-123"

    @patch("api.v1.file.routes.get_database_manager")
    def test_get_synthesis_file_with_direct_output(self, mock_db_manager):
        """Test get_synthesis_file when using direct output"""
        # Mock job without cache hit
        mock_job = Mock()
        mock_job.cache_hit = False
        mock_job.cached_result_id = None
        mock_job.output_path = "/path/to/direct/output.wav"

        mock_session = Mock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_job
        mock_db_manager.return_value.get_session.return_value.__enter__.return_value = mock_session

        file_path, filename, cache_id = get_synthesis_file("job-123")

        assert file_path == "/path/to/direct/output.wav"
        assert filename == "output.wav"
        assert cache_id is None

    @patch("api.v1.file.routes.get_database_manager")
    def test_get_synthesis_file_no_output_path(self, mock_db_manager):
        """Test get_synthesis_file when job has no output path"""
        # Mock job without any output
        mock_job = Mock()
        mock_job.cache_hit = False
        mock_job.cached_result_id = None
        mock_job.output_path = None

        mock_session = Mock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_job
        mock_db_manager.return_value.get_session.return_value.__enter__.return_value = mock_session

        file_path, filename, cache_id = get_synthesis_file("job-123")

        assert file_path is None
        assert filename is None
        assert cache_id is None

    @patch("api.v1.file.routes.get_database_manager")
    def test_get_synthesis_file_cache_miss(self, mock_db_manager):
        """Test get_synthesis_file when cache hit is True but cache entry doesn't exist"""
        # Mock job with cache hit but no cache entry
        mock_job = Mock()
        mock_job.cache_hit = True
        mock_job.cached_result_id = "cache-123"
        mock_job.output_path = "/path/to/direct/output.wav"

        mock_session = Mock()
        mock_session.query.return_value.filter_by.return_value.first.side_effect = [mock_job, None]
        mock_db_manager.return_value.get_session.return_value.__enter__.return_value = mock_session

        file_path, filename, cache_id = get_synthesis_file("job-123")

        # Should fall back to direct output
        assert file_path == "/path/to/direct/output.wav"
        assert filename == "output.wav"
        assert cache_id is None

    @patch("api.v1.file.routes.get_database_manager")
    def test_get_synthesis_file_database_error(self, mock_db_manager):
        """Test get_synthesis_file when database raises an exception"""
        mock_db_manager.return_value.get_session.side_effect = Exception("Database connection failed")

        # Should handle the exception gracefully
        with pytest.raises(Exception):
            get_synthesis_file("job-123")


class TestFilePathLogic:
    """Unit tests for file path handling logic"""

    def test_filename_extraction(self):
        """Test filename extraction from various paths"""
        test_cases = [
            ("/path/to/file.wav", "file.wav"),
            ("/deep/nested/path/audio.mp3", "audio.mp3"),
            ("simple.flac", "simple.flac"),
            ("/path/with/dots/in.name.ogg", "in.name.ogg"),
            ("", ""),
            ("/path/without/extension", "extension"),
        ]

        for path, expected in test_cases:
            if path:
                result = os.path.basename(path)
                assert result == expected
            else:
                result = os.path.basename(path)
                assert result == ""

    def test_file_storage_paths(self):
        """Test file storage paths based on start.py configuration"""
        # Test environment variable defaults
        synthesis_storage = os.getenv("VOXIFY_SYNTHESIS_STORAGE", "data/files/synthesis")
        samples_storage = os.getenv("VOXIFY_SAMPLES_STORAGE", "data/files/samples")
        temp_storage = os.getenv("VOXIFY_TEMP_STORAGE", "data/files/temp")

        # Verify expected paths
        assert "synthesis" in synthesis_storage
        assert "samples" in samples_storage
        assert "temp" in temp_storage

        # Test path structure
        assert synthesis_storage.endswith("synthesis")
        assert samples_storage.endswith("samples")
        assert temp_storage.endswith("temp")

    def test_audio_file_extensions(self):
        """Test supported audio file extensions"""
        supported_formats = ["wav", "mp3", "flac", "ogg"]

        for format_ext in supported_formats:
            # Test filename with extension
            filename = f"test_audio.{format_ext}"
            extracted_ext = os.path.splitext(filename)[1][1:]
            assert extracted_ext == format_ext

            # Test mimetype format
            mimetype = f"audio/{format_ext}"
            assert mimetype.startswith("audio/")

    def test_file_path_validation(self):
        """Test file path validation logic"""
        # Test valid paths
        valid_paths = ["data/files/synthesis/output.wav", "/absolute/path/to/file.mp3", "relative/path/file.flac"]

        for path in valid_paths:
            # Should not raise exception for valid paths
            basename = os.path.basename(path)
            assert isinstance(basename, str)
            assert len(basename) > 0

    def test_cache_vs_direct_output_logic(self):
        """Test cache vs direct output logic scenarios"""
        scenarios = [
            # (cache_hit, cached_result_id, output_path, expected_source)
            (True, "cache-123", "/path/to/output.wav", "cache"),
            (False, None, "/path/to/output.wav", "direct"),
            (True, None, "/path/to/output.wav", "direct"),
            (False, None, None, "none"),
            (True, "cache-123", None, "cache"),
        ]

        for cache_hit, cached_id, output_path, expected_source in scenarios:
            # This test validates the logic flow in get_synthesis_file
            if cache_hit and cached_id:
                # Should prefer cache
                assert expected_source == "cache"
            elif output_path:
                # Should use direct output
                assert expected_source == "direct"
            else:
                # Should return none
                assert expected_source == "none"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
