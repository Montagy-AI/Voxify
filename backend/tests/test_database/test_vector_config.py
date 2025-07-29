"""
Vector Database Configuration Tests
Comprehensive test suite for Chroma vector database functionality
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
import json

# Add the current directory to Python path to find the database module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../.."))

from database.vector_config import (
    VectorDBConfig,
    ChromaVectorDB,
    create_vector_db,
    load_config,
)


class TestVectorDBConfig:
    """Test VectorDBConfig functionality"""

    def test_vector_db_config_creation(self):
        """Test basic VectorDBConfig creation"""
        config = VectorDBConfig(
            persist_directory="/test/path",
            collection_name="test_collection",
            distance_metric="cosine",
        )

        assert config.persist_directory == "/test/path"
        assert config.collection_name == "test_collection"
        assert config.distance_metric == "cosine"
        assert config.embedding_function is None

    def test_vector_db_config_defaults(self):
        """Test VectorDBConfig default values"""
        config = VectorDBConfig()

        assert config.persist_directory == "data/chroma_db"
        assert config.collection_name == "voice_embeddings"
        assert config.distance_metric == "cosine"
        assert config.embedding_function is None

    def test_voice_embeddings_config(self):
        """Test VOICE_EMBEDDINGS_CONFIG structure"""
        config = VectorDBConfig.VOICE_EMBEDDINGS_CONFIG

        assert config["name"] == "voice_embeddings"
        assert "description" in config["metadata"]
        assert "embedding_model" in config["metadata"]
        assert "dimension" in config["metadata"]
        assert "distance_metric" in config["metadata"]
        assert "feature_type" in config["metadata"]
        assert "created_version" in config["metadata"]


class TestChromaVectorDB:
    """Test ChromaVectorDB functionality"""

    @pytest.fixture
    def temp_vector_db_path(self):
        """Create a temporary vector database path"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @patch("database.vector_config.chromadb")
    def test_chroma_vector_db_creation(self, mock_chromadb, temp_vector_db_path):
        """Test ChromaVectorDB creation"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Create VectorDBConfig
        config = VectorDBConfig(persist_directory=temp_vector_db_path)

        # Create ChromaVectorDB
        vector_db = ChromaVectorDB(config=config)

        assert vector_db.config == config
        assert vector_db.persist_directory == temp_vector_db_path
        assert vector_db.client == mock_client
        assert vector_db.collection == mock_collection
        assert vector_db.voice_embeddings_collection == mock_collection

    @patch("database.vector_config.chromadb")
    def test_chroma_vector_db_default_config(self, mock_chromadb, temp_vector_db_path):
        """Test ChromaVectorDB with default config"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Create ChromaVectorDB without config
        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        assert vector_db.config is not None
        assert vector_db.persist_directory == temp_vector_db_path
        assert vector_db.client == mock_client

    @patch("database.vector_config.chromadb")
    def test_chroma_vector_db_initialization_error(self, mock_chromadb, temp_vector_db_path):
        """Test ChromaVectorDB initialization error handling"""
        # Mock ChromaDB to raise an exception
        mock_persistent_client = Mock(side_effect=Exception("ChromaDB error"))
        mock_chromadb.PersistentClient = mock_persistent_client

        with pytest.raises(Exception, match="ChromaDB error"):
            ChromaVectorDB(persist_directory=temp_vector_db_path)

    @patch("database.vector_config.chromadb")
    def test_get_collection(self, mock_chromadb, temp_vector_db_path):
        """Test get_collection method"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        collection = vector_db.get_collection()
        assert collection == mock_collection

    @patch("database.vector_config.chromadb")
    def test_add_voice_embedding(self, mock_chromadb, temp_vector_db_path):
        """Test add_voice_embedding method"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        # Test data
        voice_sample_id = "sample-123"
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        metadata = {"user_id": "user-123", "language": "en-US"}

        # Call method
        vector_db.add_voice_embedding(voice_sample_id, embedding, metadata)

        # Verify collection.add was called
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert call_args[1]["ids"] == [voice_sample_id]
        assert call_args[1]["embeddings"] == [embedding]
        # Check that enhanced metadata was created with default values
        enhanced_metadata = call_args[1]["metadatas"][0]
        assert enhanced_metadata["user_id"] == "user-123"
        assert enhanced_metadata["language"] == "en-US"
        assert enhanced_metadata["duration"] == 0.0
        assert enhanced_metadata["quality_score"] == 0.0
        assert enhanced_metadata["sample_rate"] == 22050
        assert enhanced_metadata["is_public"] is False

    @patch("database.vector_config.chromadb")
    def test_add_voice_embedding_error(self, mock_chromadb, temp_vector_db_path):
        """Test add_voice_embedding error handling"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.add = Mock(side_effect=Exception("Add error"))
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        with pytest.raises(Exception, match="Add error"):
            vector_db.add_voice_embedding("sample-123", [0.1, 0.2, 0.3], {})

    @patch("database.vector_config.chromadb")
    def test_get_embedding(self, mock_chromadb, temp_vector_db_path):
        """Test get_embedding method"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Mock collection.get response
        mock_collection.get.return_value = {
            "ids": ["sample-123"],
            "embeddings": [[0.1, 0.2, 0.3]],
            "metadatas": [{"user_id": "user-123"}],
        }

        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        # Call method
        result = vector_db.get_embedding("sample-123")

        # Verify result
        assert result["ids"] == ["sample-123"]
        assert result["embeddings"] == [[0.1, 0.2, 0.3]]
        assert result["metadatas"] == [{"user_id": "user-123"}]

        # Verify collection.get was called
        mock_collection.get.assert_called_once_with(ids=["sample-123"], include=["embeddings", "metadatas", "documents"])

    @patch("database.vector_config.chromadb")
    def test_get_embedding_not_found(self, mock_chromadb, temp_vector_db_path):
        """Test get_embedding when embedding not found"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Mock empty collection.get response
        mock_collection.get.return_value = {
            "ids": [],
            "embeddings": [],
            "metadatas": [],
        }

        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        # Call method
        result = vector_db.get_embedding("nonexistent-123")

        # Verify empty result
        assert result["ids"] == []
        assert result["embeddings"] == []
        assert result["metadatas"] == []

    @patch("database.vector_config.chromadb")
    def test_update_embedding_metadata(self, mock_chromadb, temp_vector_db_path):
        """Test update_embedding_metadata method"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Mock collection.get response
        mock_collection.get.return_value = {
            "ids": ["sample-123"],
            "metadatas": [{"user_id": "user-123", "language": "en-US"}],
        }

        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        # Test data
        embedding_id = "sample-123"
        new_metadata = {"language": "es-ES", "quality": "high"}

        # Call method
        vector_db.update_embedding_metadata(embedding_id, new_metadata)

        # Verify collection.update was called
        mock_collection.update.assert_called_once_with(
            ids=[embedding_id],
            metadatas=[{"user_id": "user-123", "language": "es-ES", "quality": "high"}],
        )

    @patch("database.vector_config.chromadb")
    def test_delete_embedding(self, mock_chromadb, temp_vector_db_path):
        """Test delete_embedding method"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        # Call method
        vector_db.delete_embedding("sample-123")

        # Verify collection.delete was called
        mock_collection.delete.assert_called_once_with(ids=["sample-123"])

    @patch("database.vector_config.chromadb")
    def test_get_collection_count(self, mock_chromadb, temp_vector_db_path):
        """Test get_collection_count method"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Mock collection.count response
        mock_collection.count.return_value = 42
        mock_collection.metadata = {"test": "metadata"}

        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        # Call method
        result = vector_db.get_collection_count()

        # Verify result
        assert result["name"] == "voice_embeddings"
        assert result["item count"] == 42
        assert result["metadata"] == {"test": "metadata"}

        # Verify collection.count was called
        mock_collection.count.assert_called_once()

    @patch("database.vector_config.chromadb")
    def test_close(self, mock_chromadb, temp_vector_db_path):
        """Test close method"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        vector_db = ChromaVectorDB(persist_directory=temp_vector_db_path)

        # Call method
        vector_db.close()

        # Verify client.persist was called (not close)
        mock_client.persist.assert_called_once()


class TestVectorDBFunctions:
    """Test vector database utility functions"""

    @patch("database.vector_config.ChromaVectorDB")
    def test_create_vector_db(self, mock_chroma_vector_db):
        """Test create_vector_db function"""
        # Mock ChromaVectorDB
        mock_instance = Mock()
        mock_chroma_vector_db.return_value = mock_instance

        # Call function
        result = create_vector_db()

        # Verify result
        assert result == mock_instance
        mock_chroma_vector_db.assert_called_once()

    @patch("database.vector_config.load_config")
    @patch("database.vector_config.ChromaVectorDB")
    def test_create_vector_db_with_config_path(self, mock_chroma_vector_db, mock_load_config):
        """Test create_vector_db with config path"""
        # Mock load_config
        mock_load_config.return_value = {
            "persist_directory": "/test/path",
            "host": "localhost",
            "port": 8000,
        }

        # Mock ChromaVectorDB
        mock_instance = Mock()
        mock_chroma_vector_db.return_value = mock_instance

        # Call function with config path
        result = create_vector_db(config_path="/test/config.json")

        # Verify result
        assert result == mock_instance
        mock_load_config.assert_called_once_with("/test/config.json")
        mock_chroma_vector_db.assert_called_once()

    @patch("database.vector_config.json.load")
    @patch("builtins.open", create=True)
    def test_load_config_with_path(self, mock_open, mock_json_load):
        """Test load_config with config path"""
        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_json_load.return_value = {"test": "config"}

        # Call function
        result = load_config("/test/config.json")

        # Verify result
        assert result["persist_directory"] == "data/chroma_db"  # Default value
        assert result["host"] is None  # Default value
        assert result["port"] == 8000  # Default value
        mock_open.assert_called_once_with("/test/config.json", "r")
        mock_json_load.assert_called_once_with(mock_file)

    def test_load_config_without_path(self):
        """Test load_config without config path"""
        # Call function without path
        result = load_config()

        # Should return default config
        assert isinstance(result, dict)
        assert result["persist_directory"] == "data/chroma_db"
        assert result["host"] is None
        assert result["port"] == 8000


class TestVectorDBIntegration:
    """Test vector database integration scenarios"""

    @pytest.fixture
    def temp_vector_db_path(self):
        """Create a temporary vector database path"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @patch("database.vector_config.chromadb")
    def test_voice_embedding_workflow(self, mock_chromadb, temp_vector_db_path):
        """Test complete voice embedding workflow"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Mock collection responses
        mock_collection.count.return_value = 0
        mock_collection.get.return_value = {
            "ids": ["sample-123"],
            "embeddings": [[0.1, 0.2, 0.3]],
            "metadatas": [{"user_id": "user-123"}],
        }

        # Create vector database
        config = VectorDBConfig(persist_directory=temp_vector_db_path)
        vector_db = ChromaVectorDB(config=config)

        # Test initial count
        count = vector_db.get_collection_count()
        assert count["name"] == "voice_embeddings"
        assert count["item count"] == 0

        # Test adding embedding
        voice_sample_id = "sample-123"
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        metadata = {"user_id": "user-123", "language": "en-US"}

        vector_db.add_voice_embedding(voice_sample_id, embedding, metadata)
        mock_collection.add.assert_called_once()

        # Test getting embedding
        result = vector_db.get_embedding(voice_sample_id)
        assert result["ids"] == ["sample-123"]
        assert result["embeddings"] == [[0.1, 0.2, 0.3]]

        # Test updating metadata
        new_metadata = {"language": "es-ES", "quality": "high"}
        vector_db.update_embedding_metadata(voice_sample_id, new_metadata)
        mock_collection.update.assert_called_once()

        # Test deleting embedding
        vector_db.delete_embedding(voice_sample_id)
        mock_collection.delete.assert_called_once()

    @patch("database.vector_config.chromadb")
    def test_multiple_embeddings_management(self, mock_chromadb, temp_vector_db_path):
        """Test managing multiple voice embeddings"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Mock collection responses
        mock_collection.count.return_value = 3

        # Mock get to return only the requested sample
        def mock_get(ids=None, **kwargs):
            if ids and ids[0] == "sample-1":
                return {
                    "ids": ["sample-1"],
                    "embeddings": [[0.1]],
                    "metadatas": [{"user_id": "user-1"}],
                }
            return {"ids": [], "embeddings": [], "metadatas": []}

        mock_collection.get.side_effect = mock_get

        # Create vector database
        config = VectorDBConfig(persist_directory=temp_vector_db_path)
        vector_db = ChromaVectorDB(config=config)

        # Test collection count
        count = vector_db.get_collection_count()
        assert count["name"] == "voice_embeddings"
        assert count["item count"] == 3

        # Test getting multiple embeddings
        result = vector_db.get_embedding("sample-1")
        assert len(result["ids"]) == 1
        assert result["ids"][0] == "sample-1"

    @patch("database.vector_config.chromadb")
    def test_error_handling_scenarios(self, mock_chromadb, temp_vector_db_path):
        """Test error handling in vector database operations"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Create vector database
        config = VectorDBConfig(persist_directory=temp_vector_db_path)
        vector_db = ChromaVectorDB(config=config)

        # Test add embedding error
        mock_collection.add.side_effect = Exception("Add failed")
        with pytest.raises(Exception, match="Add failed"):
            vector_db.add_voice_embedding("sample-123", [0.1, 0.2, 0.3], {})

        # Test update metadata error
        mock_collection.get.return_value = {
            "ids": ["sample-123"],
            "metadatas": [{"user_id": "user-123"}],
        }
        mock_collection.update.side_effect = Exception("Update failed")
        with pytest.raises(Exception, match="Update failed"):
            vector_db.update_embedding_metadata("sample-123", {})

        # Test delete embedding error
        mock_collection.delete.side_effect = Exception("Delete failed")
        with pytest.raises(Exception, match="Delete failed"):
            vector_db.delete_embedding("sample-123")


class TestVectorDBPerformance:
    """Test vector database performance scenarios"""

    @pytest.fixture
    def temp_vector_db_path(self):
        """Create a temporary vector database path"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @patch("database.vector_config.chromadb")
    def test_large_embedding_batch(self, mock_chromadb, temp_vector_db_path):
        """Test handling large batches of embeddings"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Create vector database
        config = VectorDBConfig(persist_directory=temp_vector_db_path)
        vector_db = ChromaVectorDB(config=config)

        # Test adding multiple embeddings
        for i in range(10):
            voice_sample_id = f"sample-{i}"
            embedding = [float(j) for j in range(768)]  # 768-dimensional embedding
            metadata = {"user_id": f"user-{i}", "language": "en-US"}

            vector_db.add_voice_embedding(voice_sample_id, embedding, metadata)

        # Verify add was called 10 times
        assert mock_collection.add.call_count == 10

    @patch("database.vector_config.chromadb")
    def test_embedding_dimensions(self, mock_chromadb, temp_vector_db_path):
        """Test handling different embedding dimensions"""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_persistent_client = Mock(return_value=mock_client)
        mock_chromadb.PersistentClient = mock_persistent_client
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        # Create vector database
        config = VectorDBConfig(persist_directory=temp_vector_db_path)
        vector_db = ChromaVectorDB(config=config)

        # Test different embedding dimensions
        dimensions = [64, 128, 256, 512, 768]

        for dim in dimensions:
            voice_sample_id = f"sample-{dim}d"
            embedding = [0.1] * dim
            metadata = {"dimension": dim}

            vector_db.add_voice_embedding(voice_sample_id, embedding, metadata)

        # Verify add was called for each dimension
        assert mock_collection.add.call_count == len(dimensions)
