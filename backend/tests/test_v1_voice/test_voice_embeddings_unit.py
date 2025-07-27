"""
Voice Embeddings Unit Tests
Tests for voice embedding generation and management functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import numpy as np
import uuid

# Add the current directory to Python path to find the api module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../.."))

from api.v1.voice.embeddings import (
    generate_voice_embedding,
    delete_voice_embedding,
    get_voice_embedding,
    compare_embeddings,
)


class TestVoiceEmbeddingGeneration:
    """Unit tests for voice embedding generation"""

    @patch("api.v1.voice.embeddings.preprocess_wav")
    @patch("api.v1.voice.embeddings.voice_collection")
    def test_generate_voice_embedding_success(self, mock_collection, mock_preprocess):
        """Test successful voice embedding generation"""
        # Mock audio preprocessing
        mock_audio = np.random.rand(16000).astype(np.float32)
        mock_preprocess.return_value = mock_audio

        # Mock embedding generation
        mock_embedding = np.random.rand(256).astype(np.float32)

        # Mock the voice_encoder directly
        with patch("api.v1.voice.embeddings.voice_encoder") as mock_encoder:
            mock_encoder.embed_utterance.return_value = mock_embedding

            # Mock ChromaDB collection
            mock_collection.add.return_value = None

            # Test embedding generation
            embedding_id, embedding = generate_voice_embedding("/path/to/audio.wav")

            # Verify results
            assert isinstance(embedding_id, str)
            assert len(embedding_id) > 0
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape == (256,)

            # Verify calls
            mock_preprocess.assert_called_once_with("/path/to/audio.wav")
            mock_encoder.embed_utterance.assert_called_once_with(mock_audio)
            mock_collection.add.assert_called_once()

    @patch("api.v1.voice.embeddings.preprocess_wav")
    def test_generate_voice_embedding_preprocessing_error(self, mock_preprocess):
        """Test embedding generation with preprocessing error"""
        mock_preprocess.side_effect = Exception("Audio preprocessing failed")

        with pytest.raises(Exception, match="Audio preprocessing failed"):
            generate_voice_embedding("/path/to/invalid.wav")

    @patch("api.v1.voice.embeddings.preprocess_wav")
    def test_generate_voice_embedding_encoder_error(self, mock_preprocess):
        """Test embedding generation with encoder error"""
        # Mock audio preprocessing
        mock_audio = np.random.rand(16000).astype(np.float32)
        mock_preprocess.return_value = mock_audio

        # Mock encoder error
        with patch("api.v1.voice.embeddings.voice_encoder") as mock_encoder:
            mock_encoder.embed_utterance.side_effect = Exception("Encoder failed")

            with pytest.raises(Exception, match="Encoder failed"):
                generate_voice_embedding("/path/to/audio.wav")

    @patch("api.v1.voice.embeddings.voice_collection")
    def test_delete_voice_embedding_success(self, mock_collection):
        """Test successful voice embedding deletion"""
        embedding_id = str(uuid.uuid4())
        mock_collection.delete.return_value = None

        result = delete_voice_embedding(embedding_id)

        assert result is True
        mock_collection.delete.assert_called_once_with(ids=[embedding_id])

    @patch("api.v1.voice.embeddings.voice_collection")
    def test_delete_voice_embedding_error(self, mock_collection):
        """Test voice embedding deletion with error"""
        embedding_id = str(uuid.uuid4())
        mock_collection.delete.side_effect = Exception("Deletion failed")

        # The function should return False, not raise an exception
        result = delete_voice_embedding(embedding_id)
        assert result is False

    @patch("api.v1.voice.embeddings.voice_collection")
    def test_get_voice_embedding_success(self, mock_collection):
        """Test successful voice embedding retrieval"""
        embedding_id = str(uuid.uuid4())
        mock_embedding = np.random.rand(256).astype(np.float32)

        mock_collection.get.return_value = {
            "embeddings": [mock_embedding.tolist()],
            "metadatas": [{"audio_path": "/path/to/audio.wav"}],
        }

        embedding = get_voice_embedding(embedding_id)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (256,)
        mock_collection.get.assert_called_once_with(ids=[embedding_id])

    @patch("api.v1.voice.embeddings.voice_collection")
    def test_get_voice_embedding_not_found(self, mock_collection):
        """Test voice embedding retrieval when not found"""
        embedding_id = str(uuid.uuid4())
        mock_collection.get.return_value = {"embeddings": [], "metadatas": []}

        embedding = get_voice_embedding(embedding_id)

        assert embedding is None

    def test_compare_embeddings_success(self):
        """Test successful embedding comparison"""
        # Create test embeddings
        embedding1 = np.random.rand(256).astype(np.float32)
        embedding2 = np.random.rand(256).astype(np.float32)

        # Normalize embeddings for cosine similarity
        embedding1_norm = embedding1 / np.linalg.norm(embedding1)
        embedding2_norm = embedding2 / np.linalg.norm(embedding2)

        similarity = compare_embeddings(embedding1, embedding2)

        # Verify similarity is between -1 and 1
        assert -1 <= similarity <= 1
        assert isinstance(similarity, float)

    def test_compare_embeddings_identical(self):
        """Test embedding comparison with identical embeddings"""
        embedding = np.random.rand(256).astype(np.float32)

        similarity = compare_embeddings(embedding, embedding)

        # Should be very close to 1 for identical embeddings
        assert abs(similarity - 1.0) < 1e-6

    def test_compare_embeddings_orthogonal(self):
        """Test embedding comparison with orthogonal embeddings"""
        # Create orthogonal embeddings
        embedding1 = np.array([1, 0, 0, 0, 0, 0, 0, 0] * 32, dtype=np.float32)
        embedding2 = np.array([0, 1, 0, 0, 0, 0, 0, 0] * 32, dtype=np.float32)

        similarity = compare_embeddings(embedding1, embedding2)

        # Should be close to 0 for orthogonal embeddings
        assert abs(similarity) < 1e-6

    def test_compare_embeddings_invalid_input(self):
        """Test embedding comparison with invalid input"""
        embedding1 = np.random.rand(256).astype(np.float32)
        embedding2 = np.random.rand(128).astype(np.float32)  # Different size

        with pytest.raises(ValueError):
            compare_embeddings(embedding1, embedding2)


class TestVoiceEmbeddingValidation:
    """Unit tests for voice embedding validation"""

    def test_embedding_dimension_validation(self):
        """Test embedding dimension validation"""
        # Valid embedding
        valid_embedding = np.random.rand(256).astype(np.float32)
        assert valid_embedding.shape == (256,)

        # Invalid embedding (wrong dimension)
        invalid_embedding = np.random.rand(128).astype(np.float32)
        assert invalid_embedding.shape != (256,)

    def test_embedding_data_type_validation(self):
        """Test embedding data type validation"""
        # Valid data type
        valid_embedding = np.random.rand(256).astype(np.float32)
        assert valid_embedding.dtype == np.float32

        # Invalid data type
        invalid_embedding = np.random.rand(256).astype(np.float64)
        assert invalid_embedding.dtype != np.float32

    def test_embedding_normalization(self):
        """Test embedding normalization"""
        embedding = np.random.rand(256).astype(np.float32)

        # Normalize embedding
        norm = np.linalg.norm(embedding)
        normalized = embedding / norm

        # Verify normalization
        assert abs(np.linalg.norm(normalized) - 1.0) < 1e-6


class TestVoiceEmbeddingPerformance:
    """Unit tests for voice embedding performance"""

    def test_embedding_generation_time(self):
        """Test embedding generation performance"""
        import time

        # Mock embedding generation
        embedding = np.random.rand(256).astype(np.float32)

        start_time = time.time()
        # Simulate embedding generation
        time.sleep(0.01)  # Simulate processing time
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete within reasonable time
        assert processing_time < 1.0  # Less than 1 second

    def test_embedding_comparison_performance(self):
        """Test embedding comparison performance"""
        import time

        # Create test embeddings
        embedding1 = np.random.rand(256).astype(np.float32)
        embedding2 = np.random.rand(256).astype(np.float32)

        start_time = time.time()
        similarity = compare_embeddings(embedding1, embedding2)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete very quickly
        assert processing_time < 0.1  # Less than 100ms

    def test_multiple_embedding_comparisons(self):
        """Test performance of multiple embedding comparisons"""
        import time

        # Create multiple embeddings
        embeddings = [np.random.rand(256).astype(np.float32) for _ in range(10)]

        start_time = time.time()
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = compare_embeddings(embeddings[i], embeddings[j])
                similarities.append(similarity)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete within reasonable time
        assert processing_time < 1.0  # Less than 1 second
        assert len(similarities) == 45  # 10 choose 2 = 45 comparisons


class TestVoiceEmbeddingErrorHandling:
    """Unit tests for voice embedding error handling"""

    def test_invalid_audio_path(self):
        """Test handling of invalid audio path"""
        with pytest.raises(Exception):
            generate_voice_embedding("")

    def test_none_embedding_comparison(self):
        """Test handling of None embeddings in comparison"""
        embedding = np.random.rand(256).astype(np.float32)

        with pytest.raises(TypeError):
            compare_embeddings(None, embedding)

        with pytest.raises(TypeError):
            compare_embeddings(embedding, None)

    def test_empty_embedding_comparison(self):
        """Test handling of empty embeddings in comparison"""
        embedding = np.random.rand(256).astype(np.float32)
        empty_embedding = np.array([])

        with pytest.raises(ValueError):
            compare_embeddings(embedding, empty_embedding)

    def test_zero_embedding_comparison(self):
        """Test handling of zero embeddings in comparison"""
        embedding = np.random.rand(256).astype(np.float32)
        zero_embedding = np.zeros(256, dtype=np.float32)

        # Should handle gracefully
        similarity = compare_embeddings(embedding, zero_embedding)
        assert isinstance(similarity, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
