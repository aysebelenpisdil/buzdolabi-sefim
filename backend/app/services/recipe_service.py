import json
import os
import logging
from typing import List, Optional
from app.models.recipe import Recipe, RecipeWithMatch
from app.utils.cache import cache
from app.services.faiss_service import faiss_service
from app.services.embedding_service import embedding_service

# Setup logger
logger = logging.getLogger(__name__)


class RecipeService:
    def __init__(self):
        self.recipes: List[Recipe] = []
        self._recipes_loaded = False
    
    def _load_recipes(self):
        """Load recipes from JSON data file"""
        try:
            # Load from JSON file
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data',
                'recipes.json'
            )
            
            if not os.path.exists(data_path):
                logger.warning(f"recipes.json not found at {data_path}, using empty list")
                self.recipes = []
                return
            
            with open(data_path, 'r', encoding='utf-8') as f:
                recipes_data = json.load(f)
            
            if not recipes_data:
                self.recipes = []
                logger.info("recipes.json is empty")
                return
            
            # Filter out recipes with None values and convert to Recipe models
            valid_recipes = []
            skipped = 0
            
            for recipe in recipes_data:
                try:
                    # Check if all required fields exist and are not None
                    if (recipe.get('Title') and 
                        recipe.get('Ingredients') and 
                        recipe.get('Image_Name') and 
                        recipe.get('Cleaned_Ingredients')):
                        valid_recipes.append(Recipe(**recipe))
                    else:
                        skipped += 1
                except Exception:
                    skipped += 1
                    continue
            
            self.recipes = valid_recipes
            logger.info(f"Loaded {len(self.recipes)} recipes")
            if skipped > 0:
                logger.warning(f"Skipped {skipped} invalid recipes")
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Error loading recipes: {e}, using empty list")
            self.recipes = []
        except Exception as e:
            logger.error(f"Error loading recipes: {e}", exc_info=True)
            self.recipes = []
    
    def _ensure_loaded(self):
        """Ensure recipes are loaded (lazy loading)"""
        if not self._recipes_loaded:
            self._load_recipes()
            self._recipes_loaded = True
    
    def _count_matches(self, recipe: Recipe, user_ingredients: List[str]) -> List[str]:
        """
        Count matching ingredients between recipe and user ingredients
        
        Args:
            recipe: Recipe object
            user_ingredients: List of user ingredient names
            
        Returns:
            List of matching ingredient names
        """
        recipe_ingredients_lower = recipe.Ingredients.lower()
        matching_ingredients = []
        
        for ingredient in user_ingredients:
            if ingredient.lower() in recipe_ingredients_lower:
                matching_ingredients.append(ingredient)
        
        return matching_ingredients
    
    def _string_matching_search(self, user_ingredients: List[str]) -> List[RecipeWithMatch]:
        """
        Fallback search method using string matching
        Used when FAISS index is not available
        
        Args:
            user_ingredients: List of ingredient names
            
        Returns:
            List of RecipeWithMatch objects sorted by matching count
        """
        self._ensure_loaded()
        results = []
        
        for recipe in self.recipes:
            matching_ingredients = self._count_matches(recipe, user_ingredients)
            
            if len(matching_ingredients) > 0:
                results.append(
                    RecipeWithMatch(
                        **recipe.dict(),
                        matchingCount=len(matching_ingredients),
                        matchingIngredients=matching_ingredients
                    )
                )
        
        # Sort by matching count (descending)
        results.sort(key=lambda x: x.matchingCount, reverse=True)
        
        return results
    
    def find_suitable_recipes(
        self, 
        user_ingredients: List[str],
        use_vector_search: bool = True,
        top_k: int = 50
    ) -> List[RecipeWithMatch]:
        """
        Find recipes that match user ingredients using vector search or string matching
        
        Args:
            user_ingredients: List of ingredient names
            use_vector_search: Whether to use FAISS vector search (default: True)
            top_k: Number of top results to return (default: 50)
            
        Returns:
            List of RecipeWithMatch objects sorted by relevance
        """
        # Check cache first
        # Combine all parameters into a single dict for cache key generation
        cache_data = {
            "ingredients": sorted(user_ingredients),
            "use_vector_search": use_vector_search,
            "top_k": top_k
        }
        cache_key = cache._generate_key("recipes", cache_data)
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for ingredients: {user_ingredients}")
            return cached_result
        
        self._ensure_loaded()
        
        # Use vector search if available and requested
        if use_vector_search and faiss_service.is_loaded():
            try:
                logger.debug(f"Using vector search for ingredients: {user_ingredients}")
                
                # Search using FAISS
                distances, indices = faiss_service.search_by_ingredients(
                    ingredients=user_ingredients,
                    k=min(top_k, len(self.recipes)),
                    embedding_service=embedding_service
                )
                
                # Convert results to RecipeWithMatch
                results = []
                for idx, dist in zip(indices, distances):
                    if idx < len(self.recipes):
                        recipe = self.recipes[idx]
                        
                        # Count actual matching ingredients for display
                        matching_ingredients = self._count_matches(recipe, user_ingredients)
                        
                        results.append(
                            RecipeWithMatch(
                                **recipe.dict(),
                                matchingCount=len(matching_ingredients),
                                matchingIngredients=matching_ingredients
                            )
                        )
                
                logger.debug(f"Vector search returned {len(results)} results")
                
                # Cache result for 5 minutes
                cache.set(cache_key, results, ttl_seconds=300)
                
                return results
                
            except Exception as e:
                logger.warning(f"Vector search failed: {e}, falling back to string matching")
                # Fall through to string matching
        
        # Fallback to string matching
        logger.debug(f"Using string matching for ingredients: {user_ingredients}")
        results = self._string_matching_search(user_ingredients)
        
        # Limit results to top_k
        results = results[:top_k]
        
        # Cache result for 5 minutes
        cache.set(cache_key, results, ttl_seconds=300)
        
        return results
    
    def get_all_recipes(self, limit: int = 50, offset: int = 0) -> List[Recipe]:
        """Get all recipes with pagination"""
        self._ensure_loaded()
        return self.recipes[offset:offset + limit]
    
    def get_recipe_by_title(self, title: str) -> Optional[Recipe]:
        """Get a recipe by title"""
        self._ensure_loaded()
        for recipe in self.recipes:
            if recipe.Title == title:
                return recipe
        return None
    
    def get_total_count(self) -> int:
        """Get total number of recipes"""
        self._ensure_loaded()
        return len(self.recipes)


# Singleton instance
recipe_service = RecipeService()

