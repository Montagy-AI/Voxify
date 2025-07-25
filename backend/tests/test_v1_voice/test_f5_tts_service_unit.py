"""
F5-TTS Service Unit Tests
Tests for F5-TTS service functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
import base64
from pathlib import Path
import tempfile
import shutil

# Add the current directory to Python path to find the api module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../.."))

from api.v1.voice.f5_tts_service import (
    F5TTSService,
    VoiceCloneConfig,
    TTSConfig
)


class TestF5TTSServiceInitialization:
    """Unit tests for F5-TTS service initialization"""

    @patch("api.v1.voice.f5_tts_service.os.getenv")
    def test_service_initialization_remote(self, mock_getenv):
        """Test F5-TTS service initialization with remote mode"""
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            "F5_TTS_REMOTE_URL": "https://test-api.modal.run/synthesize",
            "F5_TTS_TIMEOUT": "120"
        }.get(key, default)
        
        service = F5TTSService(use_remote=True)
        
        assert service.use_remote is True
        assert service.device == "remote"
        assert service.initialized is True
        assert "test-api.modal.run" in service.remote_api_url

    @patch("api.v1.voice.f5_tts_service.os.getenv")
    @patch("api.v1.voice.f5_tts_service.torch")
    def test_service_initialization_local(self, mock_torch, mock_getenv):
        """Test F5-TTS service initialization with local mode"""
        # Mock torch
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"
        
        # Mock environment variables
        mock_getenv.return_value = "120"  # Return a string instead of None
        
        service = F5TTSService(use_remote=False)
        
        assert service.use_remote is False
        assert service.device == "cpu"
        assert service.initialized is False

    def test_voice_clone_config_creation(self):
        """Test VoiceCloneConfig creation"""
        config = VoiceCloneConfig(
            name="Test Clone",
            ref_audio_path="/path/to/audio.wav",
            ref_text="This is a test reference text",
            description="Test description",
            language="zh-CN"
        )
        
        assert config.name == "Test Clone"
        assert config.ref_audio_path == "/path/to/audio.wav"
        assert config.ref_text == "This is a test reference text"
        assert config.description == "Test description"
        assert config.language == "zh-CN"

    def test_tts_config_creation(self):
        """Test TTSConfig creation"""
        config = TTSConfig(
            text="Hello world",
            ref_audio_path="/path/to/audio.wav",
            ref_text="Reference text",
            language="en-US",
            speed=1.2
        )
        
        assert config.text == "Hello world"
        assert config.ref_audio_path == "/path/to/audio.wav"
        assert config.ref_text == "Reference text"
        assert config.language == "en-US"
        assert config.speed == 1.2


class TestF5TTSServiceValidation:
    """Unit tests for F5-TTS service validation"""

    @patch("api.v1.voice.f5_tts_service.os.path.exists")
    @patch("api.v1.voice.f5_tts_service.torchaudio.load")
    def test_validate_audio_file_success(self, mock_torchaudio_load, mock_exists):
        """Test successful audio file validation"""
        mock_exists.return_value = True
        
        # Mock torchaudio.load with valid duration (5 seconds at 24kHz)
        mock_audio = Mock()
        mock_audio.shape = [1, 120000]  # 5 seconds at 24kHz (valid duration)
        mock_torchaudio_load.return_value = (mock_audio, 24000)
        
        service = F5TTSService()
        is_valid, message = service.validate_audio_file("/path/to/audio.wav")
        
        assert is_valid is True
        assert "valid" in message.lower()

    @patch("api.v1.voice.f5_tts_service.os.path.exists")
    def test_validate_audio_file_not_found(self, mock_exists):
        """Test audio file validation when file doesn't exist"""
        mock_exists.return_value = False
        
        service = F5TTSService()
        is_valid, message = service.validate_audio_file("/path/to/nonexistent.wav")
        
        assert is_valid is False
        assert "not found" in message.lower()

    @patch("api.v1.voice.f5_tts_service.os.path.exists")
    @patch("api.v1.voice.f5_tts_service.torchaudio.load")
    def test_validate_audio_file_invalid_format(self, mock_torchaudio_load, mock_exists):
        """Test audio file validation with invalid format"""
        mock_exists.return_value = True
        mock_torchaudio_load.side_effect = Exception("Invalid audio format")
        
        service = F5TTSService()
        is_valid, message = service.validate_audio_file("/path/to/invalid.wav")
        
        assert is_valid is False
        assert "failed to validate" in message.lower()

    @patch("api.v1.voice.f5_tts_service.os.path.exists")
    @patch("api.v1.voice.f5_tts_service.torchaudio.load")
    def test_validate_audio_file_too_short(self, mock_torchaudio_load, mock_exists):
        """Test audio file validation with too short duration"""
        mock_exists.return_value = True
        
        # Mock torchaudio.load with very short duration
        mock_audio = Mock()
        mock_audio.shape = [1, 2400]  # 0.1 second at 24kHz (too short)
        mock_torchaudio_load.return_value = (mock_audio, 24000)
        
        service = F5TTSService()
        is_valid, message = service.validate_audio_file("/path/to/short.wav")
        
        assert is_valid is False
        assert "too short" in message.lower()


class TestF5TTSServiceRemoteOperations:
    """Unit tests for F5-TTS service remote operations"""

    @patch("api.v1.voice.f5_tts_service.requests.post")
    @patch("builtins.open", create=True)
    @patch("api.v1.voice.f5_tts_service.Path.mkdir")
    @patch("api.v1.voice.f5_tts_service.os.path.getsize")
    def test_synthesize_remote_success(self, mock_getsize, mock_mkdir, mock_open, mock_post):
        """Test successful remote synthesis"""
        # Mock file reading
        mock_audio_data = b"fake_audio_data"
        mock_open.return_value.__enter__ = Mock(return_value=Mock(read=lambda: mock_audio_data))
        mock_open.return_value.__exit__ = Mock(return_value=None)
        
        # Mock file size
        mock_getsize.return_value = 1024
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "audio_data": base64.b64encode(b"fake_output_audio").decode()
        }
        mock_post.return_value = mock_response
        
        service = F5TTSService(use_remote=True)
        config = TTSConfig(
            text="Hello world",
            ref_audio_path="/path/to/audio.wav",
            ref_text="Reference text"
        )
        
        output_path = service._synthesize_remote(config)
        
        assert output_path is not None
        assert isinstance(output_path, str)
        mock_post.assert_called_once()

    @patch("api.v1.voice.f5_tts_service.requests.post")
    @patch("builtins.open", create=True)
    @patch("api.v1.voice.f5_tts_service.Path.mkdir")
    def test_synthesize_remote_api_error(self, mock_mkdir, mock_open, mock_post):
        """Test remote synthesis with API error"""
        # Mock file reading
        mock_audio_data = b"fake_audio_data"
        mock_open.return_value.__enter__ = Mock(return_value=Mock(read=lambda: mock_audio_data))
        mock_open.return_value.__exit__ = Mock(return_value=None)
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response
        
        service = F5TTSService(use_remote=True)
        config = TTSConfig(
            text="Hello world",
            ref_audio_path="/path/to/audio.wav",
            ref_text="Reference text"
        )
        
        with pytest.raises(Exception, match="API request failed"):
            service._synthesize_remote(config)

    @patch("api.v1.voice.f5_tts_service.requests.post")
    @patch("builtins.open", create=True)
    @patch("api.v1.voice.f5_tts_service.Path.mkdir")
    def test_synthesize_remote_timeout(self, mock_mkdir, mock_open, mock_post):
        """Test remote synthesis with timeout"""
        # Mock file reading
        mock_audio_data = b"fake_audio_data"
        mock_open.return_value.__enter__ = Mock(return_value=Mock(read=lambda: mock_audio_data))
        mock_open.return_value.__exit__ = Mock(return_value=None)
        
        # Mock timeout
        mock_post.side_effect = Exception("Request timeout")
        
        service = F5TTSService(use_remote=True)
        config = TTSConfig(
            text="Hello world",
            ref_audio_path="/path/to/audio.wav",
            ref_text="Reference text"
        )
        
        with pytest.raises(Exception, match="Request timeout"):
            service._synthesize_remote(config)


class TestF5TTSServiceVoiceCloning:
    """Unit tests for F5-TTS service voice cloning"""

    @patch("api.v1.voice.f5_tts_service.F5TTSService.validate_audio_file")
    @patch("api.v1.voice.f5_tts_service.F5TTSService._synthesize_remote")
    @patch("api.v1.voice.f5_tts_service.shutil.copy2")
    @patch("api.v1.voice.f5_tts_service.Path.mkdir")
    @patch("builtins.open", create=True)
    def test_create_voice_clone_success(self, mock_open, mock_mkdir, mock_copy2, mock_synthesize, mock_validate):
        """Test successful voice clone creation"""
        # Mock validation
        mock_validate.return_value = (True, "Audio file is valid")
        
        # Mock synthesis
        mock_synthesize.return_value = "/path/to/output.wav"
        
        # Mock file operations
        mock_open.return_value.__enter__ = Mock(return_value=Mock(write=Mock()))
        mock_open.return_value.__exit__ = Mock(return_value=None)
        
        service = F5TTSService(use_remote=True)
        config = VoiceCloneConfig(
            name="Test Clone",
            ref_audio_path="/path/to/audio.wav",
            ref_text="Reference text"
        )
        
        clone_info = service.create_voice_clone(config, ["sample1", "sample2"])
        
        assert clone_info["name"] == "Test Clone"
        # The ref_audio_path will be updated to the copied path
        assert "reference.wav" in clone_info["ref_audio_path"]
        assert "id" in clone_info
        assert "created_at" in clone_info

    @patch("api.v1.voice.f5_tts_service.F5TTSService.validate_audio_file")
    @patch("api.v1.voice.f5_tts_service.shutil.copy2")
    def test_create_voice_clone_invalid_audio(self, mock_copy2, mock_validate):
        """Test voice clone creation with invalid audio"""
        # Mock validation failure
        mock_validate.return_value = (False, "Audio file is invalid")
        
        # Mock file copy to fail
        mock_copy2.side_effect = FileNotFoundError("No such file or directory")
        
        service = F5TTSService(use_remote=True)
        config = VoiceCloneConfig(
            name="Test Clone",
            ref_audio_path="/path/to/invalid.wav",
            ref_text="Reference text"
        )
        
        with pytest.raises(Exception, match="No such file or directory"):
            service.create_voice_clone(config, ["sample1"])

    @patch("api.v1.voice.f5_tts_service.Path.exists")
    @patch("builtins.open", create=True)
    def test_get_clone_info_success(self, mock_open, mock_exists):
        """Test successful clone info retrieval"""
        mock_exists.return_value = True
        
        # Mock file reading
        mock_info = {"id": "test-clone-id", "name": "Test Clone"}
        mock_open.return_value.__enter__ = Mock(return_value=Mock(read=lambda: json.dumps(mock_info)))
        mock_open.return_value.__exit__ = Mock(return_value=None)
        
        service = F5TTSService(use_remote=True)
        
        clone_id = "test-clone-id"
        info = service.get_clone_info(clone_id)
        
        assert info == mock_info

    @patch("api.v1.voice.f5_tts_service.Path.exists")
    def test_get_clone_info_not_found(self, mock_exists):
        """Test clone info retrieval when not found"""
        mock_exists.return_value = False
        
        service = F5TTSService(use_remote=True)
        
        clone_id = "nonexistent-clone-id"
        
        with pytest.raises(ValueError, match="Voice clone not found"):
            service.get_clone_info(clone_id)

    @patch("api.v1.voice.f5_tts_service.Path.exists")
    @patch("api.v1.voice.f5_tts_service.shutil.rmtree")
    def test_delete_clone_success(self, mock_rmtree, mock_exists):
        """Test successful clone deletion"""
        mock_exists.return_value = True
        
        service = F5TTSService(use_remote=True)
        
        clone_id = "test-clone-id"
        
        result = service.delete_clone(clone_id)
        
        assert result is True
        mock_rmtree.assert_called_once()

    @patch("api.v1.voice.f5_tts_service.Path.exists")
    def test_delete_clone_not_found(self, mock_exists):
        """Test clone deletion when not found"""
        mock_exists.return_value = False
        
        service = F5TTSService(use_remote=True)
        
        clone_id = "nonexistent-clone-id"
        
        result = service.delete_clone(clone_id)
        
        assert result is False


class TestF5TTSServiceErrorHandling:
    """Unit tests for F5-TTS service error handling"""

    def test_invalid_config_creation(self):
        """Test creation of invalid configurations"""
        # Test missing required fields
        with pytest.raises(TypeError):
            VoiceCloneConfig()  # Missing required arguments
        
        with pytest.raises(TypeError):
            TTSConfig()  # Missing required arguments

    def test_invalid_audio_path_handling(self):
        """Test handling of invalid audio paths"""
        service = F5TTSService()
        
        # Test empty path
        is_valid, message = service.validate_audio_file("")
        assert is_valid is False
        
        # Test None path
        is_valid, message = service.validate_audio_file(None)
        assert is_valid is False

    def test_invalid_text_handling(self):
        """Test handling of invalid text input"""
        service = F5TTSService()
        
        # Test empty text
        config = TTSConfig(
            text="",
            ref_audio_path="/path/to/audio.wav",
            ref_text="Reference text"
        )
        
        # Should handle empty text gracefully
        assert config.text == ""

    def test_invalid_language_handling(self):
        """Test handling of invalid language codes"""
        config = VoiceCloneConfig(
            name="Test Clone",
            ref_audio_path="/path/to/audio.wav",
            ref_text="Reference text",
            language="invalid-language"
        )
        
        # Should accept any language code
        assert config.language == "invalid-language"


class TestF5TTSServicePerformance:
    """Unit tests for F5-TTS service performance"""

    def test_service_initialization_performance(self):
        """Test service initialization performance"""
        import time
        
        start_time = time.time()
        service = F5TTSService(use_remote=True)
        end_time = time.time()
        
        initialization_time = end_time - start_time
        
        # Should initialize quickly
        assert initialization_time < 1.0  # Less than 1 second

    def test_config_creation_performance(self):
        """Test configuration creation performance"""
        import time
        
        start_time = time.time()
        for _ in range(100):
            config = VoiceCloneConfig(
                name="Test Clone",
                ref_audio_path="/path/to/audio.wav",
                ref_text="Reference text"
            )
        end_time = time.time()
        
        creation_time = end_time - start_time
        
        # Should create configs quickly
        assert creation_time < 1.0  # Less than 1 second for 100 configs

    @patch("api.v1.voice.f5_tts_service.os.path.exists")
    @patch("api.v1.voice.f5_tts_service.torchaudio.load")
    def test_validation_performance(self, mock_torchaudio_load, mock_exists):
        """Test audio validation performance"""
        import time
        
        mock_exists.return_value = True
        mock_audio = Mock()
        mock_audio.shape = [1, 24000]
        mock_torchaudio_load.return_value = (mock_audio, 24000)
        
        service = F5TTSService()
        
        start_time = time.time()
        for _ in range(10):
            service.validate_audio_file("/path/to/audio.wav")
        end_time = time.time()
        
        validation_time = end_time - start_time
        
        # Should validate quickly
        assert validation_time < 1.0  # Less than 1 second for 10 validations


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 