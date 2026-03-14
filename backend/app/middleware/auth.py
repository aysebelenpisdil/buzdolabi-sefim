from fastapi import Request, HTTPException, Depends
from typing import Optional
from app.services.auth_service import auth_service


async def get_current_user(request: Request) -> dict:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Giriş yapmanız gerekiyor")

    user = await auth_service.validate_session(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Oturum süresi dolmuş, tekrar giriş yapın")

    return user


async def get_optional_user(request: Request) -> Optional[dict]:
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None
    return await auth_service.validate_session(session_id)
