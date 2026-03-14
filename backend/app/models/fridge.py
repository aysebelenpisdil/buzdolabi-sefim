from pydantic import BaseModel
from typing import List


class Ingredient(BaseModel):
    name: str


class FridgeRequest(BaseModel):
    ingredients: List[str]


class FridgeResponse(BaseModel):
    success: bool
    message: str
    ingredients: List[str]

