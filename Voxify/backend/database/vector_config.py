"""
Voxify Vector Database Configuration
Chroma Collections Setup for Voice Embeddings and Text Similarity
"""

import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional, Any
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class VectorDBConfig:
    """Configuration for Chroma vector database collections"""
    
    # Collection configurations
    VOICE_EMBEDDINGS_CONFIG = {
        "name": "voice_embeddings",
        "metadata": {
            "description": "Voice sample embeddings for similarity search and voice matching",
            "embedding_model": "wav2vec2-base-960h",  # Facebook's wav2vec2 model
            "dimension": 768,
            "distance_metric": "cosine",
            "feature_type": "voice_spectral",
            "created_version": "1.0"
        }
    }
    
    SPEAKER_EMBEDDINGS_CONFIG = {
        "name": "speaker_embeddings", 
        "metadata": {
            "description": "Speaker identity embeddings for voice cloning and authentication",
            "embedding_model": "resemblyzer",  # Resemblyzer speaker verification
            "dimension": 256,
            "distance_metric": "cosine",
            "feature_type": "speaker_identity",
            "created_version": "1.0"
        }
    }
    
    TEXT_EMBEDDINGS_CONFIG = {
        "name": "text_embeddings",
        "metadata": {
            "description": "Text embeddings for synthesis caching and similar text matching",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "dimension": 384,
            "distance_metric": "cosine", 
            "feature_type": "text_semantic",
            "created_version": "1.0"
        }
    }
    
    # Quality embeddings for content moderation and filtering
    QUALITY_EMBEDDINGS_CONFIG = {
        "name": "quality_embeddings",
        "metadata": {
            "description": "Audio quality and content classification embeddings",
            "embedding_model": "audio_quality_classifier",
            "dimension": 128,
            "distance_metric": "euclidean",
            "feature_type": "quality_metrics",
            "created_version": "1.0"
        }
    }

class ChromaVectorDB:
    """Chroma vector database manager for Voxify platform"""
    
    def __init__(self, 
                 persist_directory: str = "data/chroma_db",
                 host: Optional[str] = None,
                 port: Optional[int] = None):
        """
        Initialize Chroma vector database client
        
        Parameters
        ----------
        persist_directory : str
            Local directory for persistent storage
        host : str, optional
            Remote Chroma server host (for production deployment)
        port : int, optional
            Remote Chroma server port
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client
        if host and port:
            # Remote Chroma server configuration
            self.client = chromadb.HttpClient(host=host, port=port)
            logger.info(f"Connected to remote Chroma server at {host}:{port}")
        else:
            # Local persistent storage
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            logger.info(f"Initialized local Chroma database at {self.persist_directory}")
        
        # Initialize collections
        self.collections = {}
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize all required collections"""
        configs = [
            VectorDBConfig.VOICE_EMBEDDINGS_CONFIG,
            VectorDBConfig.SPEAKER_EMBEDDINGS_CONFIG,
            VectorDBConfig.TEXT_EMBEDDINGS_CONFIG,
            VectorDBConfig.QUALITY_EMBEDDINGS_CONFIG
        ]
        
        for config in configs:
            collection_name = config["name"]
            try:
                # Get or create collection
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata=config["metadata"]
                )
                self.collections[collection_name] = collection
                logger.info(f"Initialized collection: {collection_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize collection {collection_name}: {str(e)}")
                raise
    
    def get_collection(self, collection_name: str):
        """Get a specific collection by name"""
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' not found")
        return self.collections[collection_name]
    
    def add_voice_embedding(self, 
                           voice_sample_id: str,
                           embedding: List[float],
                           metadata: Dict[str, Any]) -> None:
        """
        Add voice embedding to the voice_embeddings collection
        
        Parameters
        ----------
        voice_sample_id : str
            Unique identifier for the voice sample (UUID)
        embedding : List[float]
            Voice feature vector (768 dimensions)
        metadata : Dict[str, Any]
            Associated metadata for the voice sample
        """
        collection = self.get_collection("voice_embeddings")
        
        # Prepare document text for search
        document = f"{metadata.get('name', '')} {metadata.get('description', '')} {metadata.get('language', '')}"
        
        # Enhanced metadata with additional fields
        enhanced_metadata = {
            "user_id": metadata.get("user_id"),
            "language": metadata.get("language", "en-US"),
            "duration": float(metadata.get("duration", 0.0)),
            "quality_score": float(metadata.get("quality_score", 0.0)),
            "sample_rate": int(metadata.get("sample_rate", 22050)),
            "gender": metadata.get("gender"),
            "age_group": metadata.get("age_group"),
            "accent": metadata.get("accent"),
            "is_public": metadata.get("is_public", False),
            "created_at": metadata.get("created_at")
        }
        
        # Remove None values
        enhanced_metadata = {k: v for k, v in enhanced_metadata.items() if v is not None}
        
        collection.add(
            ids=[voice_sample_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[enhanced_metadata]
        )
        
        logger.debug(f"Added voice embedding for sample: {voice_sample_id}")
    
    def add_speaker_embedding(self,
                             speaker_embedding_id: str,
                             voice_sample_id: str,
                             embedding: List[float],
                             metadata: Dict[str, Any]) -> None:
        """
        Add speaker identity embedding to the speaker_embeddings collection
        
        Parameters
        ----------
        speaker_embedding_id : str
            Unique identifier for this speaker embedding
        voice_sample_id : str
            Reference to the source voice sample
        embedding : List[float]
            Speaker identity vector (256 dimensions)
        metadata : Dict[str, Any]
            Associated metadata
        """
        collection = self.get_collection("speaker_embeddings")
        
        document = f"Speaker identity for voice sample {voice_sample_id}"
        
        enhanced_metadata = {
            "voice_sample_id": voice_sample_id,
            "user_id": metadata.get("user_id"),
            "confidence_score": float(metadata.get("confidence_score", 0.0)),
            "gender": metadata.get("gender"),
            "age_estimate": metadata.get("age_estimate"),
            "accent_type": metadata.get("accent_type"),
            "speaker_verification_model": metadata.get("model_version", "resemblyzer-v1"),
            "created_at": metadata.get("created_at")
        }
        
        enhanced_metadata = {k: v for k, v in enhanced_metadata.items() if v is not None}
        
        collection.add(
            ids=[speaker_embedding_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[enhanced_metadata]
        )
        
        logger.debug(f"Added speaker embedding: {speaker_embedding_id}")
    
    def add_text_embedding(self,
                          text_hash: str,
                          embedding: List[float],
                          metadata: Dict[str, Any]) -> None:
        """
        Add text embedding for synthesis caching and similarity
        
        Parameters
        ----------
        text_hash : str
            Hash of the text content
        embedding : List[float]
            Text semantic vector (384 dimensions)
        metadata : Dict[str, Any]
            Text and synthesis metadata
        """
        collection = self.get_collection("text_embeddings")
        
        # Use actual text content as document
        document = metadata.get("text_content", "")
        
        enhanced_metadata = {
            "text_hash": text_hash,
            "text_length": int(metadata.get("text_length", len(document))),
            "language": metadata.get("language", "en-US"),
            "voice_model_id": metadata.get("voice_model_id"),
            "synthesis_job_id": metadata.get("synthesis_job_id"),
            "has_cache": metadata.get("has_cache", False),
            "word_count": int(metadata.get("word_count", 0)),
            "complexity_score": float(metadata.get("complexity_score", 0.0)),
            "created_at": metadata.get("created_at")
        }
        
        enhanced_metadata = {k: v for k, v in enhanced_metadata.items() if v is not None}
        
        collection.add(
            ids=[text_hash],
            embeddings=[embedding],
            documents=[document],
            metadatas=[enhanced_metadata]
        )
        
        logger.debug(f"Added text embedding for hash: {text_hash}")
    
    def search_similar_voices(self,
                             query_embedding: List[float],
                             user_id: Optional[str] = None,
                             language: Optional[str] = None,
                             min_quality: Optional[float] = None,
                             top_k: int = 10) -> Dict[str, List]:
        """
        Search for similar voice samples
        
        Parameters
        ----------
        query_embedding : List[float]
            Query voice embedding vector
        user_id : str, optional
            Filter by specific user
        language : str, optional
            Filter by language
        min_quality : float, optional
            Minimum quality score threshold
        top_k : int
            Number of results to return
            
        Returns
        -------
        Dict[str, List]
            Search results with IDs, distances, and metadata
        """
        collection = self.get_collection("voice_embeddings")
        
        # Build filter conditions
        where_conditions = {}
        if user_id:
            where_conditions["user_id"] = user_id
        if language:
            where_conditions["language"] = language
        if min_quality is not None:
            where_conditions["quality_score"] = {"$gte": min_quality}
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_conditions if where_conditions else None,
            include=["metadatas", "distances", "documents"]
        )
        
        return results
    
    def search_similar_speakers(self,
                               query_embedding: List[float],
                               user_id: Optional[str] = None,
                               min_confidence: Optional[float] = None,
                               top_k: int = 5) -> Dict[str, List]:
        """Search for similar speakers based on identity embeddings"""
        collection = self.get_collection("speaker_embeddings")
        
        where_conditions = {}
        if user_id:
            where_conditions["user_id"] = user_id
        if min_confidence is not None:
            where_conditions["confidence_score"] = {"$gte": min_confidence}
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_conditions if where_conditions else None,
            include=["metadatas", "distances", "documents"]
        )
        
        return results
    
    def search_similar_texts(self,
                            query_embedding: List[float],
                            voice_model_id: Optional[str] = None,
                            language: Optional[str] = None,
                            similarity_threshold: float = 0.95,
                            top_k: int = 5) -> Dict[str, List]:
        """
        Search for similar texts for synthesis caching
        
        Parameters
        ----------
        query_embedding : List[float]
            Query text embedding vector
        voice_model_id : str, optional
            Filter by specific voice model
        language : str, optional
            Filter by language
        similarity_threshold : float
            Minimum similarity threshold for cache hits
        top_k : int
            Number of results to return
        """
        collection = self.get_collection("text_embeddings")
        
        where_conditions = {}
        if voice_model_id:
            where_conditions["voice_model_id"] = voice_model_id
        if language:
            where_conditions["language"] = language
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_conditions if where_conditions else None,
            include=["metadatas", "distances", "documents"]
        )
        
        # Filter by similarity threshold (distance < 1 - threshold)
        distance_threshold = 1.0 - similarity_threshold
        filtered_results = {
            "ids": [[]],
            "distances": [[]],
            "metadatas": [[]],
            "documents": [[]]
        }
        
        if results["ids"] and results["ids"][0]:
            for i, distance in enumerate(results["distances"][0]):
                if distance <= distance_threshold:
                    filtered_results["ids"][0].append(results["ids"][0][i])
                    filtered_results["distances"][0].append(distance)
                    filtered_results["metadatas"][0].append(results["metadatas"][0][i])
                    filtered_results["documents"][0].append(results["documents"][0][i])
        
        return filtered_results
    
    def update_embedding_metadata(self,
                                 collection_name: str,
                                 embedding_id: str,
                                 new_metadata: Dict[str, Any]) -> None:
        """Update metadata for an existing embedding"""
        collection = self.get_collection(collection_name)
        
        # Get current record
        current = collection.get(ids=[embedding_id], include=["metadatas"])
        if not current["ids"]:
            raise ValueError(f"Embedding {embedding_id} not found in {collection_name}")
        
        # Merge metadata
        current_metadata = current["metadatas"][0]
        updated_metadata = {**current_metadata, **new_metadata}
        
        collection.update(
            ids=[embedding_id],
            metadatas=[updated_metadata]
        )
        
        logger.debug(f"Updated metadata for {embedding_id} in {collection_name}")
    
    def delete_embedding(self, collection_name: str, embedding_id: str) -> None:
        """Delete an embedding from a collection"""
        collection = self.get_collection(collection_name)
        collection.delete(ids=[embedding_id])
        logger.debug(f"Deleted embedding {embedding_id} from {collection_name}")
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        collection = self.get_collection(collection_name)
        count = collection.count()
        
        return {
            "name": collection_name,
            "count": count,
            "metadata": collection.metadata
        }
    
    def cleanup_expired_cache(self, days_old: int = 30) -> int:
        """
        Clean up old text embeddings used for caching
        
        Parameters
        ----------
        days_old : int
            Remove embeddings older than this many days
            
        Returns
        -------
        int
            Number of embeddings cleaned up
        """
        from datetime import datetime, timedelta
        
        collection = self.get_collection("text_embeddings")
        cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
        
        # Get all records older than cutoff
        all_records = collection.get(include=["metadatas"])
        old_ids = []
        
        for i, metadata in enumerate(all_records["metadatas"]):
            created_at = metadata.get("created_at")
            if created_at and created_at < cutoff_date:
                old_ids.append(all_records["ids"][i])
        
        # Delete old records
        if old_ids:
            collection.delete(ids=old_ids)
            logger.info(f"Cleaned up {len(old_ids)} old text embeddings")
        
        return len(old_ids)
    
    def close(self):
        """Close database connections and persist data"""
        if hasattr(self.client, 'persist'):
            self.client.persist()
        logger.info("Vector database connections closed and data persisted")

# Factory function for easy initialization
def create_vector_db(config_path: str = None) -> ChromaVectorDB:
    """
    Create and initialize vector database instance
    
    Parameters
    ----------
    config_path : str, optional
        Path to configuration file (for future use)
        
    Returns
    -------
    ChromaVectorDB
        Initialized vector database instance
    """
    # Default configuration from environment variables
    persist_dir = os.getenv("VECTOR_DB_PATH", "data/chroma_db")
    host = os.getenv("CHROMA_HOST")
    port = int(os.getenv("CHROMA_PORT", 8000)) if os.getenv("CHROMA_PORT") else None
    
    return ChromaVectorDB(
        persist_directory=persist_dir,
        host=host,
        port=port
    ) 