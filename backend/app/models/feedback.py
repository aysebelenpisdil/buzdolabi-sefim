from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class InteractionCreate(BaseModel):
    recipe_title: str
    interaction_type: Literal["like", "skip", "view", "cook"]
    context_ingredients: Optional[List[str]] = None


class ConsumptionCreate(BaseModel):
    recipe_title: str
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"]
    portion_size: float = Field(default=1.0, ge=0.25, le=5.0)
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class InteractionResponse(BaseModel):
    id: int
    recipe_title: str
    interaction_type: str
    created_at: str


class ConsumptionResponse(BaseModel):
    id: int
    recipe_title: str
    consumed_at: str
    meal_type: str
    portion_size: float
    rating: Optional[int] = None
    notes: Optional[str] = None


class UserFeatures(BaseModel):
    user_id: str
    email: str
    total_likes: int
    total_skips: int
    total_cooked: int
    avg_portion: Optional[float]
    preferred_meal_type: Optional[str]
    weekly_repeat_count: int
    like_skip_ratio: Optional[float]
    top_liked_recipes: List[str]
    weekly_repeats: List[str]
