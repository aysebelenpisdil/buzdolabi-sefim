from fastapi import APIRouter, Response, Depends, HTTPException
import logging
from app.models.auth import (
    MagicLinkRequest, MagicLinkVerifyRequest,
    MagicLinkResponse, UserResponse, SessionInfo,
)
from app.services.auth_service import auth_service
from app.services.email_service import send_magic_link
from app.middleware.auth import get_current_user
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(body: MagicLinkRequest):
    user = await auth_service.create_or_get_user(body.email)
    token = await auth_service.generate_magic_link(user["id"])

    logger.info(f"Magic link requested for {body.email}")

    if settings.SMTP_ENABLED:
        if not send_magic_link(body.email, token):
            raise HTTPException(
                status_code=503,
                detail="E-posta gönderilemedi. Lütfen daha sonra tekrar deneyin.",
            )
        dev_token = None
    else:
        dev_token = token if settings.NODE_ENV == "development" else None

    return MagicLinkResponse(
        message="Giriş bağlantısı e-posta adresinize gönderildi",
        dev_token=dev_token,
    )


@router.post("/verify", response_model=SessionInfo)
async def verify_magic_link(body: MagicLinkVerifyRequest, response: Response):
    user = await auth_service.verify_magic_link(body.token)
    if not user:
        raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş bağlantı")

    session_id = await auth_service.create_session(user["id"])

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=(settings.NODE_ENV != "development"),
        max_age=settings.SESSION_EXPIRY_DAYS * 24 * 3600,
    )

    session_data = await auth_service.validate_session(session_id)

    return SessionInfo(
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            display_name=user.get("display_name"),
            created_at=user["created_at"],
        ),
        expires_at=session_data["session_expires_at"],
    )


@router.get("/me", response_model=SessionInfo)
async def get_me(user: dict = Depends(get_current_user)):
    return SessionInfo(
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            display_name=user.get("display_name"),
            created_at=user["created_at"],
        ),
        expires_at=user["session_expires_at"],
    )


@router.post("/logout")
async def logout(response: Response, user: dict = Depends(get_current_user)):
    response.delete_cookie("session_id")
    logger.info(f"User {user['email']} logged out")
    return {"message": "Çıkış yapıldı"}
