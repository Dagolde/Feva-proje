"""FastAPI dependency injection — current user and RBAC."""
from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Decode JWT and load the corresponding User from the database.
    
    Checks for token in:
    1. Authorization header (Bearer token)
    2. HTTP-only cookie (for web dashboard)
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to get token from cookie if not in Authorization header
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise credentials_exc
    
    try:
        payload = decode_token(token)
    except JWTError:
        raise credentials_exc

    if payload.get("type") != "access":
        raise credentials_exc

    sub: str | None = payload.get("sub")
    if sub is None:
        raise credentials_exc

    try:
        user_id = uuid.UUID(sub)
    except ValueError:
        raise credentials_exc

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exc

    return user


def require_role(*roles: str) -> Callable:
    """Return a FastAPI dependency that enforces role membership.

    Usage::

        @router.get("/admin/users")
        async def list_users(user: User = Depends(require_role("admin"))):
            ...
    """

    async def _check_role(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        role_name: str = current_user.role.name if current_user.role else ""
        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check_role
