"""
Embedding Service
Handles recipe vectorization using sentence-transformers
"""

import os
import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.models.recipe import Recipe

# Setup logger
logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings from recipe text
    Uses sentence-transformers model (English-only)
    """
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self._model_loaded = False
    
    def _load_model(self):
        """Lazy load the embedding model (only when needed)"""
        if not self._model_loaded:
            logger.info(f"Loading embedding model: {self.model_name}...")
            try:
                self.model = SentenceTransformer(self.model_name)
                self._model_loaded = True
                logger.info(f"Embedding model loaded successfully (dimension: {self.dimension})")
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}", exc_info=True)
                raise RuntimeError(f"Failed to load embedding model '{self.model_name}': {e}") from e
    
    def _prepare_recipe_text(self, recipe: Recipe) -> str:
        """
        Combine recipe fields into a single text for embedding
        Format: Title + Ingredients + Instructions
        """
        parts = []
        
        # Title (most important)
        if recipe.Title:
            parts.append(recipe.Title)
        
        # Ingredients (cleaned version preferred)
        ingredients_text = recipe.Cleaned_Ingredients or recipe.Ingredients
        if ingredients_text:
            # Remove Python list syntax if present
            ingredients_clean = ingredients_text.replace('[', '').replace(']', '').replace("'", '')
            parts.append(f"Ingredients: {ingredients_clean}")
        
        # Instructions (if available)
        if recipe.Instructions:
            # Truncate very long instructions (keep first 500 words)
            instructions = recipe.Instructions
            words = instructions.split()
            if len(words) > 500:
                instructions = ' '.join(words[:500]) + '...'
            parts.append(f"Instructions: {instructions}")
        
        return ' '.join(parts)
    
    def encode_recipe(self, recipe: Recipe) -> np.ndarray:
        """
        Generate embedding for a single recipe
        
        Args:
            recipe: Recipe object
            
        Returns:
            numpy array of shape (dimension,)
        """
        if not self._model_loaded:
            self._load_model()
        
        recipe_text = self._prepare_recipe_text(recipe)
        embedding = self.model.encode(recipe_text, convert_to_numpy=True)
        
        return embedding
    
    def encode_recipes_batch(self, recipes: List[Recipe], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple recipes (batch processing)
        More efficient than encoding one by one
        
        Args:
            recipes: List of Recipe objects
            batch_size: Number of recipes to process at once
            
        Returns:
            numpy array of shape (num_recipes, dimension)
        """
        if not self._model_loaded:
            self._load_model()
        
        # Prepare all recipe texts
        recipe_texts = [self._prepare_recipe_text(recipe) for recipe in recipes]
        
        # Encode in batches for efficiency
        embeddings = self.model.encode(
            recipe_texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        
        return embeddings
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for arbitrary text (e.g., user query)
        
        Args:
            text: Input text string
            
        Returns:
            numpy array of shape (dimension,)
        """
        if not self._model_loaded:
            self._load_model()
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "loaded": self._model_loaded
        }


# Singleton instance
embedding_service = EmbeddingService()



