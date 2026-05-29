"""Pydantic schemas for authentication endpoints."""
from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
    totp_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    user_id: str
    lga_code: str | None = None
    ward: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class TOTPSetupResponse(BaseModel):
    secret: str
    qr_uri: str
    backup_codes: list[str]


class TOTPVerifyRequest(BaseModel):
    totp_code: str
