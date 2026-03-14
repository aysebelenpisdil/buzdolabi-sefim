from fastapi import APIRouter, HTTPException
from app.models.fridge import FridgeRequest, FridgeResponse

router = APIRouter(prefix="/fridge", tags=["fridge"])


@router.post("/ingredients", response_model=FridgeResponse)
async def save_ingredients(request: FridgeRequest):
    """
    Save fridge ingredients (placeholder - will be connected to database later)
    """
    try:
        # TODO: Save to database when implemented
        return FridgeResponse(
            success=True,
            message="Ingredients saved",
            ingredients=request.ingredients
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save ingredients: {str(e)}")


@router.get("/ingredients", response_model=dict)
async def get_ingredients():
    """
    Get saved fridge ingredients (placeholder - will be connected to database later)
    """
    try:
        # TODO: Retrieve from database when implemented
        return {"ingredients": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ingredients: {str(e)}")

