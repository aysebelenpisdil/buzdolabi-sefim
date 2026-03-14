from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class MagicLinkRequest(BaseModel):
    email: str = Field(..., min_length=5, pattern=r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class MagicLinkVerifyRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    created_at: str


class SessionInfo(BaseModel):
    user: UserResponse
    expires_at: str


class MagicLinkResponse(BaseModel):
    message: str
    dev_token: Optional[str] = None
