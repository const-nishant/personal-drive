"""Semantic indexing service using FAISS and Sentence Transformers."""

import logging
import os
import pickle
from threading import Lock
from typing import List, Optional, Tuple
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

logger = logging.getLogger(__name__)


class SemanticIndexer:
    """Service for semantic indexing and search using FAISS."""

    def __init__(self):
        """Initialize the semantic indexer with model and FAISS index."""
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.id_map: dict = {}  # file_id → FAISS vector ID mapping
        self.reverse_id_map: dict = {}  # FAISS vector ID → file_id mapping
        self.next_vector_id: int = 0  # Next available vector ID
        self.index_lock = Lock()
        self._initialize()

    def _initialize(self):
        """Initialize model and load or create FAISS index."""
        logger.info(f"Loading model: {Config.MODEL_NAME}")
        self.model = SentenceTransformer(Config.MODEL_NAME)

        # Create index directory if it doesn't exist
        os.makedirs(Config.INDEX_DIR, exist_ok=True)

        index_path = Config.get_index_path()
        meta_path = Config.get_meta_path()

        # Load or create FAISS index
        if os.path.exists(index_path):
            logger.info(f"Loading existing index from {index_path}")
            self.index = faiss.read_index(index_path)

            # Load id_map metadata
            if os.path.exists(meta_path):
                with open(meta_path, "rb") as f:
                    metadata = pickle.load(f)
                    # Handle both old format (list) and new format (dict)
                    if isinstance(metadata, list):
                        # Migrate from old format
                        logger.info("Migrating from old id_map format to new format")
                        self.id_map = {file_id: idx for idx, file_id in enumerate(metadata)}
                        self.reverse_id_map = {idx: file_id for idx, file_id in enumerate(metadata)}
                        self.next_vector_id = len(metadata)
                    else:
                        # New format
                        self.id_map = metadata.get("id_map", {})
                        self.reverse_id_map = metadata.get("reverse_id_map", {})
                        self.next_vector_id = metadata.get("next_vector_id", len(self.id_map))
                logger.info(f"Loaded {len(self.id_map)} indexed documents")
            else:
                logger.warning("Index exists but id_map not found. Starting fresh.")
                self.id_map = {}
                self.reverse_id_map = {}
                self.next_vector_id = 0
        else:
            logger.info("Creating new FAISS index with IndexIDMap for efficient deletion")
            # Create FAISS index with L2 distance wrapped in IndexIDMap for deletion support
            base_index = faiss.IndexFlatL2(Config.EMBEDDING_DIM)
            self.index = faiss.IndexIDMap(base_index)
            self.id_map = {}
            self.reverse_id_map = {}
            self.next_vector_id = 0
            logger.info("New index created successfully with IndexIDMap")

    def index_document(self, file_id: str, text: str) -> Optional[int]:
        """
        Index a document with its text content.

        Args:
            file_id: Unique file identifier
            text: Text content to index

        Returns:
            Vector ID (FAISS index position) if indexed successfully, None if already indexed or failed
        """
        if not text or not text.strip():
            logger.warning(f"Empty text for file {file_id}, skipping indexing")
            return None

        # Check if already indexed
        if file_id in self.id_map:
            logger.info(f"Document {file_id} already indexed, returning existing vector ID")
            # Return the existing vector ID
            return self.id_map[file_id]

        try:
            # Generate embedding
            embedding = self.model.encode(
                text.strip(),
                convert_to_numpy=True,
                normalize_embeddings=True
            ).reshape(1, -1)

            # Thread-safe index update
            with self.index_lock:
                # Get next vector ID
                vector_id = self.next_vector_id
                self.next_vector_id += 1

                # Add to FAISS index with ID mapping
                # IndexIDMap requires numpy array of IDs
                vector_ids = np.array([vector_id], dtype=np.int64)
                self.index.add_with_ids(embedding, vector_ids)

                # Store metadata mapping
                self.id_map[file_id] = vector_id
                self.reverse_id_map[vector_id] = file_id

                # Persist to disk
                self._save_index()

            logger.info(f"Indexed document {file_id} with vector ID {vector_id}")
            return vector_id

        except Exception as e:
            logger.error(f"Indexing failed for {file_id}: {str(e)}")
            raise

    def search(self, query: str, k: int = 5) -> List[str]:
        """
        Search for similar documents.

        Args:
            query: Search query text
            k: Number of results to return

        Returns:
            List of file IDs ordered by similarity
        """
        if not query or not query.strip():
            return []

        # Check if index is initialized
        if self.index is None or self.index.ntotal == 0:
            return []

        try:
            # Generate query embedding
            query_embedding = self.model.encode(
                query.strip(),
                convert_to_numpy=True,
                normalize_embeddings=True
            ).reshape(1, -1)

            # Search in FAISS (thread-safe read)
            with self.index_lock:
                k = min(k, self.index.ntotal)
                if k == 0:
                    return []
                distances, vector_ids = self.index.search(query_embedding, k)

            # Map FAISS vector IDs to file_ids
            # FAISS returns -1 for invalid/removed IDs
            file_ids = []
            for vector_id in vector_ids[0]:
                if vector_id >= 0 and vector_id in self.reverse_id_map:
                    file_id = self.reverse_id_map[vector_id]
                    file_ids.append(file_id)

            logger.info(
                f"Search returned {len(file_ids)} results for query: {query[:50]}..."
            )
            return file_ids

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise

    def remove_document(self, file_id: str) -> bool:
        """
        Remove a document from the index using IndexIDMap's efficient deletion.

        Args:
            file_id: File ID to remove

        Returns:
            True if found and removed, False otherwise
        """
        if file_id not in self.id_map:
            logger.warning(f"Document {file_id} not found in index")
            return False

        try:
            with self.index_lock:
                # Get vector ID for this file
                vector_id = self.id_map[file_id]

                # Remove from FAISS index using remove_ids (efficient with IndexIDMap)
                vector_ids_to_remove = np.array([vector_id], dtype=np.int64)
                self.index.remove_ids(vector_ids_to_remove)

                # Remove from metadata mappings
                del self.id_map[file_id]
                del self.reverse_id_map[vector_id]

                # Persist to disk
                self._save_index()

            logger.info(f"Removed document {file_id} (vector ID {vector_id}) from index")
            return True

        except Exception as e:
            logger.error(f"Failed to remove document {file_id}: {str(e)}")
            return False

    def _save_index(self):
        """Save FAISS index and metadata to disk."""
        try:
            index_path = Config.get_index_path()
            meta_path = Config.get_meta_path()

            faiss.write_index(self.index, index_path)
            # Save metadata in new format
            metadata = {
                "id_map": self.id_map,
                "reverse_id_map": self.reverse_id_map,
                "next_vector_id": self.next_vector_id,
            }
            with open(meta_path, "wb") as f:
                pickle.dump(metadata, f)

            logger.debug(f"Saved index to {index_path} and metadata to {meta_path}")
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}")
            raise

    def get_stats(self) -> dict:
        """
        Get index statistics.

        Returns:
            Dictionary with index statistics
        """
        return {
            "index_size": self.index.ntotal if self.index else 0,
            "documents_indexed": len(self.id_map),
            "model": Config.MODEL_NAME,
            "embedding_dimension": Config.EMBEDDING_DIM,
            "index_type": "IndexIDMap(IndexFlatL2)" if self.index else "None",
        }

