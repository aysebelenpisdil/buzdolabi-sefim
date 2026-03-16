from fastapi import APIRouter, HTTPException, Depends
from app.models.fridge import FridgeRequest, FridgeResponse
from app.middleware.auth import get_current_user
from app.services.database_service import database_service

router = APIRouter(prefix="/fridge", tags=["fridge"])


@router.get("/ingredients", response_model=dict)
async def get_ingredients(user: dict = Depends(get_current_user)):
    ingredients = await database_service.get_fridge_ingredients(user["id"])
    return {"ingredients": ingredients}


@router.post("/ingredients", response_model=FridgeResponse)
async def save_ingredients(request: FridgeRequest, user: dict = Depends(get_current_user)):
    await database_service.save_fridge_ingredients(user["id"], request.ingredients)
    return FridgeResponse(
        success=True,
        message="Ingredients saved",
        ingredients=request.ingredients
    )

