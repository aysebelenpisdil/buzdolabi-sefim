from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from app.models.feedback import (
    InteractionCreate, ConsumptionCreate, UserFeatures,
    InteractionResponse, ConsumptionResponse,
)
from app.services.database_service import database_service
from app.middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/interaction", response_model=InteractionResponse)
async def record_interaction(body: InteractionCreate, user: dict = Depends(get_current_user)):
    row_id = await database_service.record_interaction(
        user_id=user["id"],
        recipe_title=body.recipe_title,
        interaction_type=body.interaction_type,
        context_ingredients=body.context_ingredients,
    )
    logger.info(f"[{user['email']}] {body.interaction_type} -> {body.recipe_title}")
    return InteractionResponse(
        id=row_id,
        recipe_title=body.recipe_title,
        interaction_type=body.interaction_type,
        created_at="now",
    )


@router.post("/consumption", response_model=ConsumptionResponse)
async def log_consumption(body: ConsumptionCreate, user: dict = Depends(get_current_user)):
    row_id = await database_service.log_consumption(
        user_id=user["id"],
        recipe_title=body.recipe_title,
        meal_type=body.meal_type,
        portion_size=body.portion_size,
        rating=body.rating,
        notes=body.notes,
    )
    logger.info(f"[{user['email']}] consumed {body.recipe_title} ({body.meal_type}, {body.portion_size}x)")
    return ConsumptionResponse(
        id=row_id,
        recipe_title=body.recipe_title,
        consumed_at="now",
        meal_type=body.meal_type,
        portion_size=body.portion_size,
        rating=body.rating,
        notes=body.notes,
    )


@router.get("/features", response_model=UserFeatures)
async def get_features(user: dict = Depends(get_current_user)):
    features = await database_service.get_user_features(user["id"])
    return UserFeatures(**features)


@router.get("/history")
async def get_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
):
    interactions = await database_service.get_interaction_history(user["id"], limit, offset)
    return {"interactions": interactions, "count": len(interactions)}


@router.get("/consumption-history")
async def get_consumption_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
):
    logs = await database_service.get_consumption_history(user["id"], limit, offset)
    return {"consumption_logs": logs, "count": len(logs)}


@router.get("/weekly-repeats")
async def get_weekly_repeats(user: dict = Depends(get_current_user)):
    repeats = await database_service.get_weekly_repeats(user["id"])
    return {"weekly_repeats": repeats, "count": len(repeats)}


@router.delete("/interaction/{interaction_id}", status_code=204)
async def delete_interaction(
    interaction_id: int,
    user: dict = Depends(get_current_user),
):
    deleted = await database_service.delete_interaction(user["id"], interaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Etkileşim bulunamadı")


@router.get("/recipe-status/{recipe_title}")
async def get_recipe_status(recipe_title: str, user: dict = Depends(get_current_user)):
    status = await database_service.get_recipe_interaction_status(user["id"], recipe_title)
    return status
