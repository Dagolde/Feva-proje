"""Authentication endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    TOTPSetupResponse,
    TOTPVerifyRequest,
    TokenResponse,
)
from app.services import auth_service

router = APIRouter()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    ip = _client_ip(request)

    # 1. Look up user first to check lockout before attempting password verify
    user = await auth_service.get_user_by_username(db, body.username)

    if user is not None and user.locked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Account temporarily locked.",
        )

    # 2. Verify credentials (also handles failed_attempts + audit)
    authenticated_user = await auth_service.authenticate_user(
        db, body.username, body.password, ip_address=ip
    )
    if authenticated_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # 3. Re-check lockout (may have just been triggered by this attempt)
    if authenticated_user.locked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Account temporarily locked.",
        )

    # 4. TOTP check
    if authenticated_user.totp_enabled:
        if body.totp_code is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="TOTP code required",
            )
        if not auth_service.verify_totp(authenticated_user, body.totp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TOTP code",
            )

    # 5. Issue tokens + write success audit
    tokens = auth_service.issue_tokens(authenticated_user)

    try:
        audit = AuditLog(
            user_id=authenticated_user.id,
            operation="login",
            entity_type="user",
            entity_id=str(authenticated_user.id),
            detail={"username": authenticated_user.username},
            ip_address=ip,
        )
        db.add(audit)
        await db.commit()
    except Exception:
        await db.rollback()

    # Set HTTP-only cookies for web dashboard access
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=tokens.model_dump())
    
    # Access token cookie (8 hours)
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=tokens.expires_in,
        path="/",
    )
    
    # Refresh token cookie (30 days)
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 days
        path="/",
    )
    
    return response


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    # Get refresh token from body or cookie
    refresh_token = body.refresh_token or request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )
    
    try:
        tokens = await auth_service.refresh_access_token(db, refresh_token)
        
        # Set updated cookies
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=tokens.model_dump())
        
        # Access token cookie (8 hours)
        response.set_cookie(
            key="access_token",
            value=tokens.access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=tokens.expires_in,
            path="/",
        )
        
        # Refresh token cookie (30 days)
        response.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=60 * 60 * 24 * 30,  # 30 days
            path="/",
        )
        
        return response
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    body: RefreshRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    # Get refresh token from body or cookie
    refresh_token = body.refresh_token or request.cookies.get("refresh_token")

    if refresh_token:
        try:
            # Best-effort: revoke the refresh token if we can decode the user
            from app.core.security import decode_token
            from jose import JWTError
            access_token = request.cookies.get("access_token")
            if access_token:
                try:
                    payload = decode_token(access_token)
                    import uuid as _uuid
                    user_id = _uuid.UUID(payload.get("sub", ""))
                    await auth_service.logout_user(
                        db,
                        user_id=user_id,
                        refresh_token=refresh_token,
                        ip_address=_client_ip(request),
                    )
                except Exception:
                    pass
        except Exception:
            pass

    from fastapi.responses import Response
    response = Response(status_code=status.HTTP_200_OK)
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response


# ---------------------------------------------------------------------------
# POST /auth/totp/setup  (Admin only)
# ---------------------------------------------------------------------------


@router.post("/totp/setup", response_model=TOTPSetupResponse)
async def totp_setup(
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TOTPSetupResponse:
    return await auth_service.setup_totp(db, current_user)


# ---------------------------------------------------------------------------
# POST /auth/totp/verify
# ---------------------------------------------------------------------------


@router.post("/totp/verify")
async def totp_verify(
    body: TOTPVerifyRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, bool]:
    valid = auth_service.verify_totp(current_user, body.totp_code)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )
    return {"verified": True}
