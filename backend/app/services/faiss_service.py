"""
FAISS Service
Handles vector similarity search using FAISS index
"""

import os
import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Tuple, Optional
import logging
from app.config import settings
from app.models.recipe import Recipe

# Setup logger
logger = logging.getLogger(__name__)


class FAISSService:
    """
    Service for FAISS-based similarity search
    Manages index creation, loading, and searching
    """
    
    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.embeddings: Optional[np.ndarray] = None
        self.recipes: Optional[List[Recipe]] = None
        self.index_path = Path(__file__).parent.parent.parent / settings.FAISS_INDEX_PATH
        self.metadata_path = self.index_path.parent / 'recipe_index_metadata.json'
        self.dimension = settings.EMBEDDING_DIMENSION
        self._index_loaded = False
    
    def _create_index(self) -> faiss.Index:
        """
        Create a new FAISS index based on configuration
        """
        index_type = settings.FAISS_INDEX_TYPE
        
        if index_type == "IndexFlatL2":
            index = faiss.IndexFlatL2(self.dimension)
        elif index_type == "IndexFlatIP":
            index = faiss.IndexFlatIP(self.dimension)
        else:
            # Default to IndexFlatL2
            logger.warning(f"Unknown index type '{index_type}', using IndexFlatL2 as default")
            index = faiss.IndexFlatL2(self.dimension)
        
        return index
    
    def build_index(self, embeddings: np.ndarray, recipes: List[Recipe]) -> bool:
        """
        Build FAISS index from embeddings
        
        Args:
            embeddings: NumPy array of shape (num_recipes, dimension)
            recipes: List of Recipe objects (for metadata)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Building FAISS index...")
            logger.info(f"  Embeddings shape: {embeddings.shape}")
            logger.info(f"  Recipes count: {len(recipes)}")
            
            # Validate inputs
            if embeddings.shape[0] != len(recipes):
                raise ValueError(f"Embeddings count ({embeddings.shape[0]}) doesn't match recipes count ({len(recipes)})")
            
            if embeddings.shape[1] != self.dimension:
                raise ValueError(f"Embedding dimension ({embeddings.shape[1]}) doesn't match expected ({self.dimension})")
            
            # Create index
            index = self._create_index()
            
            # Normalize embeddings for L2 distance (optional, but recommended)
            # For cosine similarity, we'd normalize, but for L2 we keep as-is
            embeddings_normalized = embeddings.astype('float32')
            
            # Add vectors to index
            index.add(embeddings_normalized)
            
            logger.info("FAISS index built successfully")
            logger.info(f"  Index type: {type(index).__name__}")
            logger.info(f"  Total vectors: {index.ntotal}")
            
            # Save index
            self.index = index
            self.embeddings = embeddings_normalized
            self.recipes = recipes
            self._index_loaded = True
            
            # Save to disk
            self._save_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}", exc_info=True)
            return False
    
    def _save_index(self):
        """Save index and metadata to disk"""
        try:
            # Ensure directory exists
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            logger.info(f"Index saved to: {self.index_path}")
            
            # Save metadata
            metadata = {
                "index_type": settings.FAISS_INDEX_TYPE,
                "metric": settings.FAISS_METRIC,
                "dimension": self.dimension,
                "num_vectors": self.index.ntotal,
                "recipes": [
                    {
                        "index": i,
                        "title": recipe.Title,
                        "image_name": recipe.Image_Name
                    }
                    for i, recipe in enumerate(self.recipes)
                ]
            }
            
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metadata saved to: {self.metadata_path}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}", exc_info=True)
            raise
    
    def load_index(self) -> bool:
        """
        Load FAISS index from disk
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.index_path.exists():
                logger.warning(f"FAISS index file not found: {self.index_path}")
                logger.info("Vector search will not be available. Using fallback search methods.")
                return False
            
            # Check file size (basic validation)
            file_size = self.index_path.stat().st_size
            if file_size == 0:
                logger.error(f"FAISS index file is empty: {self.index_path}")
                logger.warning("Vector search will not be available. Using fallback search methods.")
                return False
            
            logger.debug(f"Loading FAISS index from {self.index_path} (size: {file_size} bytes)")
            
            # Load FAISS index
            try:
                self.index = faiss.read_index(str(self.index_path))
            except Exception as e:
                logger.error(
                    f"Failed to read FAISS index file. The file may be corrupted: {e}",
                    exc_info=True
                )
                logger.warning("Vector search will not be available. Using fallback search methods.")
                return False
            
            # Validate index
            if self.index.ntotal == 0:
                logger.warning("FAISS index contains no vectors")
                return False
            
            if self.index.d != self.dimension:
                logger.error(
                    f"Index dimension mismatch: expected {self.dimension}, "
                    f"got {self.index.d}. Index may be incompatible."
                )
                logger.warning("Vector search will not be available. Using fallback search methods.")
                return False
            
            logger.info(f"FAISS index loaded successfully from: {self.index_path}")
            logger.info(f"  Index type: {type(self.index).__name__}")
            logger.info(f"  Total vectors: {self.index.ntotal}")
            logger.info(f"  Dimension: {self.dimension}")
            
            # Load metadata
            if self.metadata_path.exists():
                try:
                    with open(self.metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Validate metadata
                    if metadata.get('num_vectors') != self.index.ntotal:
                        logger.warning(
                            f"Metadata vector count ({metadata.get('num_vectors')}) "
                            f"doesn't match index ({self.index.ntotal})"
                        )
                    else:
                        logger.info(f"Metadata loaded: {metadata.get('num_vectors', 'unknown')} vectors")
                except Exception as e:
                    logger.warning(f"Failed to load metadata: {e}")
            
            # Load embeddings (for reference, not required for search)
            embeddings_path = self.index_path.parent / 'recipe_embeddings.npy'
            if embeddings_path.exists():
                try:
                    self.embeddings = np.load(embeddings_path)
                    logger.debug(f"Embeddings loaded: {self.embeddings.shape}")
                except Exception as e:
                    logger.debug(f"Failed to load embeddings file (optional): {e}")
            
            self._index_loaded = True
            return True
            
        except FileNotFoundError:
            logger.warning(f"FAISS index file not found: {self.index_path}")
            logger.info("Vector search will not be available. Using fallback search methods.")
            return False
        except PermissionError as e:
            logger.error(f"Permission denied accessing FAISS index file: {e}")
            logger.warning("Vector search will not be available. Using fallback search methods.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading FAISS index: {e}", exc_info=True)
            logger.warning("Vector search will not be available. Using fallback search methods.")
            return False
    
    def is_loaded(self) -> bool:
        """
        Check if FAISS index is loaded and ready for search
        
        Returns:
            True if index is loaded, False otherwise
        """
        return self._index_loaded and self.index is not None
    
    def _ensure_index_loaded(self):
        """
        Ensure index is loaded before search
        
        Raises:
            RuntimeError: If index cannot be loaded
        """
        if not self._index_loaded:
            logger.debug("Index not loaded, attempting to load...")
            if not self.load_index():
                error_msg = (
                    f"FAISS index not available. "
                    f"Index file expected at: {self.index_path}. "
                    f"Please build the index first or check the file path."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)
    
    def search(
        self, 
        query_vector: np.ndarray, 
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding of shape (dimension,)
            k: Number of results to return
            
        Returns:
            Tuple of (distances, indices)
            - distances: Array of shape (k,) - L2 distances (lower is better)
            - indices: Array of shape (k,) - Recipe indices
            
        Raises:
            RuntimeError: If index is not loaded
            ValueError: If query vector has wrong shape or dimension
        """
        self._ensure_index_loaded()
        
        # Validate query vector
        if query_vector is None or query_vector.size == 0:
            raise ValueError("Query vector cannot be empty")
        
        if query_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Query vector dimension mismatch: expected {self.dimension}, "
                f"got {query_vector.shape[0]}"
            )
        
        # Validate k
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        
        if k > self.index.ntotal:
            logger.warning(
                f"Requested k={k} is greater than total vectors ({self.index.ntotal}). "
                f"Returning {self.index.ntotal} results."
            )
            k = self.index.ntotal
        
        try:
            # Reshape query to (1, dimension) for FAISS
            query_reshaped = query_vector.reshape(1, -1).astype('float32')
            
            # Search
            distances, indices = self.index.search(query_reshaped, k)
            
            logger.debug(f"FAISS search completed: {len(indices[0])} results")
            
            # Return flattened results
            return distances[0], indices[0]
            
        except Exception as e:
            logger.error(f"Error during FAISS search: {e}", exc_info=True)
            raise RuntimeError(f"FAISS search failed: {e}") from e
    
    def search_by_text(
        self, 
        text: str, 
        k: int = 10,
        embedding_service=None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for recipes similar to a text query
        
        Args:
            text: Query text (e.g., "chicken pasta recipe")
            k: Number of results to return
            embedding_service: EmbeddingService instance to encode text
            
        Returns:
            Tuple of (distances, indices)
            
        Raises:
            ValueError: If text is empty or embedding_service is None
            RuntimeError: If encoding or search fails
        """
        if embedding_service is None:
            error_msg = "embedding_service is required for text search. Please provide an EmbeddingService instance."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not text or not text.strip():
            error_msg = "Search text cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            logger.debug(f"Encoding text query: '{text[:50]}...' (truncated)")
            # Encode text to embedding
            query_embedding = embedding_service.encode_text(text)
            
            # Search using embedding
            return self.search(query_embedding, k)
            
        except Exception as e:
            logger.error(f"Error in text search: {e}", exc_info=True)
            raise RuntimeError(f"Text search failed: {e}") from e
    
    def search_by_ingredients(
        self,
        ingredients: List[str],
        k: int = 10,
        embedding_service=None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for recipes similar to a list of ingredients
        
        Args:
            ingredients: List of ingredient names
            k: Number of results to return
            embedding_service: EmbeddingService instance to encode text
            
        Returns:
            Tuple of (distances, indices)
            
        Raises:
            ValueError: If ingredients list is empty
            RuntimeError: If search fails
        """
        if not ingredients or len(ingredients) == 0:
            error_msg = "Ingredients list cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # Create query text from ingredients
            query_text = f"Recipe with ingredients: {', '.join(ingredients)}"
            logger.debug(f"Searching by ingredients: {ingredients}")
            
            return self.search_by_text(query_text, k, embedding_service)
            
        except Exception as e:
            logger.error(f"Error in ingredient search: {e}", exc_info=True)
            raise RuntimeError(f"Ingredient search failed: {e}") from e
    
    def get_index_info(self) -> dict:
        """Get information about the loaded index"""
        if not self.index:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "index_type": type(self.index).__name__,
            "num_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_path": str(self.index_path),
            "metadata_path": str(self.metadata_path)
        }


# Singleton instance
faiss_service = FAISSService()

