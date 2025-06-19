import json
import hashlib
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os
from flask import Flask

# Add the backend and backend/api directories to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from api.v1.job.routes import (
    validate_synthesis_job_data,
    generate_text_hash,
    error_response,
    success_response
)

class TestJobValidation:
    """Unit tests for job data validation logic"""
    
    def test_validate_synthesis_job_data_valid(self):
        """Test validation with valid job data"""
        data = {
            'text_content': 'Hello world',
            'voice_model_id': 'vm_123',
            'speed': 1.0,
            'pitch': 1.0,
            'volume': 1.0,
            'output_format': 'wav',
            'sample_rate': 22050
        }
        
        is_valid, errors = validate_synthesis_job_data(data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_synthesis_job_data_missing_required(self):
        """Test validation with missing required fields"""
        data = {
            'speed': 1.0,
            'pitch': 1.0
        }
        
        is_valid, errors = validate_synthesis_job_data(data)
        assert is_valid is False
        assert 'text_content' in errors
        assert 'voice_model_id' in errors
        assert errors['text_content'] == 'Text content is required'
        assert errors['voice_model_id'] == 'Voice model ID is required'
    
    def test_validate_synthesis_job_data_invalid_speed(self):
        """Test validation with invalid speed values"""
        test_cases = [
            {'speed': 0.0, 'expected_error': 'Speed must be between 0.1 and 3.0'},
            {'speed': 3.1, 'expected_error': 'Speed must be between 0.1 and 3.0'},
            {'speed': -1.0, 'expected_error': 'Speed must be between 0.1 and 3.0'},
            {'speed': 'invalid', 'expected_error': 'Speed must be a valid number'}
        ]
        
        for case in test_cases:
            data = {
                'text_content': 'Hello world',
                'voice_model_id': 'vm_123',
                'speed': case['speed']
            }
            
            is_valid, errors = validate_synthesis_job_data(data)
            assert is_valid is False
            assert 'speed' in errors
            assert errors['speed'] == case['expected_error']
    
    def test_validate_synthesis_job_data_invalid_pitch(self):
        """Test validation with invalid pitch values"""
        test_cases = [
            {'pitch': 0.0, 'expected_error': 'Pitch must be between 0.1 and 3.0'},
            {'pitch': 3.1, 'expected_error': 'Pitch must be between 0.1 and 3.0'},
            {'pitch': -1.0, 'expected_error': 'Pitch must be between 0.1 and 3.0'},
            {'pitch': 'invalid', 'expected_error': 'Pitch must be a valid number'}
        ]
        
        for case in test_cases:
            data = {
                'text_content': 'Hello world',
                'voice_model_id': 'vm_123',
                'pitch': case['pitch']
            }
            
            is_valid, errors = validate_synthesis_job_data(data)
            assert is_valid is False
            assert 'pitch' in errors
            assert errors['pitch'] == case['expected_error']
    
    def test_validate_synthesis_job_data_invalid_volume(self):
        """Test validation with invalid volume values"""
        test_cases = [
            {'volume': -0.1, 'expected_error': 'Volume must be between 0.0 and 2.0'},
            {'volume': 2.1, 'expected_error': 'Volume must be between 0.0 and 2.0'},
            {'volume': 'invalid', 'expected_error': 'Volume must be a valid number'}
        ]
        
        for case in test_cases:
            data = {
                'text_content': 'Hello world',
                'voice_model_id': 'vm_123',
                'volume': case['volume']
            }
            
            is_valid, errors = validate_synthesis_job_data(data)
            assert is_valid is False
            assert 'volume' in errors
            assert errors['volume'] == case['expected_error']
    
    def test_validate_synthesis_job_data_invalid_output_format(self):
        """Test validation with invalid output format"""
        data = {
            'text_content': 'Hello world',
            'voice_model_id': 'vm_123',
            'output_format': 'invalid_format'
        }
        
        is_valid, errors = validate_synthesis_job_data(data)
        assert is_valid is False
        assert 'output_format' in errors
        assert errors['output_format'] == 'Output format must be one of: wav, mp3, flac, ogg'
    
    def test_validate_synthesis_job_data_valid_output_formats(self):
        """Test validation with valid output formats"""
        valid_formats = ['wav', 'mp3', 'flac', 'ogg']
        
        for format_type in valid_formats:
            data = {
                'text_content': 'Hello world',
                'voice_model_id': 'vm_123',
                'output_format': format_type
            }
            
            is_valid, errors = validate_synthesis_job_data(data)
            assert is_valid is True
            assert 'output_format' not in errors
    
    def test_validate_synthesis_job_data_invalid_sample_rate(self):
        """Test validation with invalid sample rates"""
        test_cases = [
            {'sample_rate': 1000, 'expected_error': 'Sample rate must be one of: 8000, 16000, 22050, 44100, 48000'},
            {'sample_rate': 44101, 'expected_error': 'Sample rate must be one of: 8000, 16000, 22050, 44100, 48000'},
            {'sample_rate': 'invalid', 'expected_error': 'Sample rate must be a valid integer'}
        ]
        
        for case in test_cases:
            data = {
                'text_content': 'Hello world',
                'voice_model_id': 'vm_123',
                'sample_rate': case['sample_rate']
            }
            
            is_valid, errors = validate_synthesis_job_data(data)
            assert is_valid is False
            assert 'sample_rate' in errors
            assert errors['sample_rate'] == case['expected_error']
    
    def test_validate_synthesis_job_data_valid_sample_rates(self):
        """Test validation with valid sample rates"""
        valid_rates = [8000, 16000, 22050, 44100, 48000]
        
        for rate in valid_rates:
            data = {
                'text_content': 'Hello world',
                'voice_model_id': 'vm_123',
                'sample_rate': rate
            }
            
            is_valid, errors = validate_synthesis_job_data(data)
            assert is_valid is True
            assert 'sample_rate' not in errors
    
    def test_validate_synthesis_job_data_update_mode(self):
        """Test validation in update mode (is_update=True)"""
        # In update mode, required fields are not checked
        data = {
            'speed': 1.5,
            'pitch': 1.2
        }
        
        is_valid, errors = validate_synthesis_job_data(data, is_update=True)
        assert is_valid is True
        assert len(errors) == 0

class TestTextHashGeneration:
    """Unit tests for text hash generation logic"""
    
    def test_generate_text_hash_basic(self):
        """Test basic text hash generation"""
        text = "Hello world"
        hash_result = generate_text_hash(text)
        
        # Hash should be consistent for same input
        hash_result2 = generate_text_hash(text)
        assert hash_result == hash_result2
        
        # Hash should be a valid SHA256 hex string
        assert len(hash_result) == 64
        assert all(c in '0123456789abcdef' for c in hash_result)
    
    def test_generate_text_hash_with_config(self):
        """Test text hash generation with configuration"""
        text = "Hello world"
        config = {"speed": 1.0, "pitch": 1.0}
        
        hash_result = generate_text_hash(text, config)
        
        # Hash should be different from text-only hash
        text_only_hash = generate_text_hash(text)
        assert hash_result != text_only_hash
        
        # Hash should be consistent for same text and config
        hash_result2 = generate_text_hash(text, config)
        assert hash_result == hash_result2
    
    def test_generate_text_hash_config_order_independent(self):
        """Test that hash is independent of config key order"""
        text = "Hello world"
        config1 = {"speed": 1.0, "pitch": 1.0}
        config2 = {"pitch": 1.0, "speed": 1.0}
        
        hash1 = generate_text_hash(text, config1)
        hash2 = generate_text_hash(text, config2)
        
        # Hashes should be the same regardless of key order
        assert hash1 == hash2
    
    def test_generate_text_hash_empty_config(self):
        """Test text hash generation with empty config"""
        text = "Hello world"
        
        hash_with_none = generate_text_hash(text, None)
        hash_with_empty = generate_text_hash(text, {})
        
        # Both should produce the same hash
        assert hash_with_none == hash_with_empty

class TestResponseFormatters:
    """Unit tests for response formatting functions"""
    
    def test_error_response_basic(self):
        """Test basic error response formatting"""
        app = Flask(__name__)
        with app.app_context():
            with patch('api.v1.job.routes.datetime') as mock_datetime:
                mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
                response, status_code = error_response("Test error message")
                assert status_code == 400
                assert response.json['success'] is False
                assert response.json['error']['message'] == "Test error message"
                assert response.json['error']['code'] == "ERROR_400"
                assert response.json['error']['timestamp'] == "2024-01-01T12:00:00"
    
    def test_error_response_with_custom_code(self):
        """Test error response with custom error code"""
        app = Flask(__name__)
        with app.app_context():
            response, status_code = error_response("Test error", "CUSTOM_ERROR")
            assert response.json['error']['code'] == "CUSTOM_ERROR"
    
    def test_error_response_with_details(self):
        """Test error response with additional details"""
        app = Flask(__name__)
        with app.app_context():
            details = {"field": "text_content", "value": "invalid"}
            response, status_code = error_response("Validation failed", details=details)
            assert response.json['error']['details'] == details
    
    def test_error_response_custom_status(self):
        """Test error response with custom status code"""
        app = Flask(__name__)
        with app.app_context():
            response, status_code = error_response("Not found", status_code=404)
            assert status_code == 404
            assert response.json['error']['code'] == "ERROR_404"
    
    def test_success_response_basic(self):
        """Test basic success response formatting"""
        app = Flask(__name__)
        with app.app_context():
            with patch('api.v1.job.routes.datetime') as mock_datetime:
                mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
                response, status_code = success_response()
                assert status_code == 200
                assert response.json['success'] is True
                assert response.json['timestamp'] == "2024-01-01T12:00:00"
    
    def test_success_response_with_data(self):
        """Test success response with data"""
        app = Flask(__name__)
        with app.app_context():
            data = {"id": "job_123", "status": "pending"}
            response, status_code = success_response(data=data)
            assert response.json['data'] == data
    
    def test_success_response_with_message(self):
        """Test success response with message"""
        app = Flask(__name__)
        with app.app_context():
            response, status_code = success_response(message="Job created successfully")
            assert response.json['message'] == "Job created successfully"
    
    def test_success_response_with_meta(self):
        """Test success response with metadata"""
        app = Flask(__name__)
        with app.app_context():
            meta = {"pagination": {"total": 100, "page": 1}}
            response, status_code = success_response(meta=meta)
            assert response.json['meta'] == meta
    
    def test_success_response_custom_status(self):
        """Test success response with custom status code"""
        app = Flask(__name__)
        with app.app_context():
            response, status_code = success_response(status_code=201)
            assert status_code == 201

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 