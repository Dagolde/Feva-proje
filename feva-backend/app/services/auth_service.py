"""Authentication business logic."""
from __future__ import annotations

import secrets
import string
import uuid
from datetime import UTC, datetime

import pyotp
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.auth import TOTPSetupResponse, TokenResponse

# ---------------------------------------------------------------------------
# In-memory stores (Phase 1 MVP — replaced by DB in Phase 2)
# ---------------------------------------------------------------------------

# Maps user_id (str) → set of active refresh token JTIs
_refresh_tokens: dict[str, set[str]] = {}

# Maps user_id (str) → list of bcrypt-hashed backup codes
_backup_codes: dict[str, list[str]] = {}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_LOCKOUT_THRESHOLD = 5
_LOCKOUT_WINDOW_MINUTES = 15
_ACCESS_EXPIRES_SECONDS = 60 * 60 * 8  # 8 hours (matches ACCESS_TOKEN_EXPIRE_MINUTES=480)


async def _write_audit(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | None,
    operation: str,
    detail: dict | None = None,
    ip_address: str | None = None,
) -> None:
    entry = AuditLog(
        user_id=user_id,
        operation=operation,
        entity_type="user",
        entity_id=str(user_id) if user_id else None,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    await db.flush()


# ---------------------------------------------------------------------------
# Core auth
# ---------------------------------------------------------------------------


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(User).where(User.username == username).options(selectinload(User.role))
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.role))
    )
    return result.scalar_one_or_none()


async def record_failed_attempt(
    db: AsyncSession,
    user: User,
    ip_address: str | None = None,
) -> None:
    """Increment failed_attempts; lock account if threshold reached; write audit entry.
    
    Implements 15-minute rate limiting window:
    - If no window is active or window expired, start a new window
    - If within window and threshold reached (5 attempts), lock account
    - If window expired, reset counter and start new window
    """
    from datetime import timedelta
    
    now = datetime.now(UTC)
    
    # Check if we need to reset the window
    if user.failed_attempts_window_start is None:
        # Start new window
        user.failed_attempts_window_start = now
        user.failed_attempts = 1
    else:
        # Check if window has expired (15 minutes)
        window_start = user.failed_attempts_window_start
        if isinstance(window_start, str):
            from dateutil import parser
            window_start = parser.parse(window_start)
        
        window_elapsed = now - window_start
        if window_elapsed > timedelta(minutes=_LOCKOUT_WINDOW_MINUTES):
            # Window expired, reset and start new window
            user.failed_attempts_window_start = now
            user.failed_attempts = 1
        else:
            # Within window, increment counter
            user.failed_attempts = (user.failed_attempts or 0) + 1
    
    # Lock account if threshold reached
    if user.failed_attempts >= _LOCKOUT_THRESHOLD:
        user.locked_at = now

    await _write_audit(
        db,
        user_id=user.id,
        operation="login_failed",
        detail={"failed_attempts": user.failed_attempts},
        ip_address=ip_address,
    )
    await db.commit()


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
    ip_address: str | None = None,
) -> User | None:
    """Verify credentials.  Returns User on success, None on failure.

    Side-effects: increments failed_attempts on failure; writes audit log.
    Does NOT check lockout — callers must check user.locked_at separately.
    """
    user = await get_user_by_username(db, username)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        await record_failed_attempt(db, user, ip_address=ip_address)
        return None

    # Successful auth — reset failed_attempts and window
    user.failed_attempts = 0
    user.failed_attempts_window_start = None
    await db.commit()
    return user


def issue_tokens(user: User) -> TokenResponse:
    """Create access + refresh token pair and register the refresh JTI."""
    jti = str(uuid.uuid4())
    user_id_str = str(user.id)

    # Eager-load role name — caller must ensure user.role is loaded
    role_name: str = user.role.name if user.role else "enumerator"

    # Use first assigned LGA as the primary lga_code for the mobile client
    lga_code: str | None = (
        user.lga_assignment[0] if user.lga_assignment else None
    )

    ward: str | None = user.ward_assignment or None

    access_token = create_access_token(
        {"sub": user_id_str, "role": role_name, "jti": str(uuid.uuid4())}
    )
    refresh_token = create_refresh_token(
        {"sub": user_id_str, "role": role_name, "jti": jti}
    )

    # Register JTI
    _refresh_tokens.setdefault(user_id_str, set()).add(jti)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=_ACCESS_EXPIRES_SECONDS,
        role=role_name,
        user_id=user_id_str,
        lga_code=lga_code,
        ward=ward,
    )


async def refresh_access_token(
    db: AsyncSession,
    refresh_token: str,
) -> TokenResponse:
    """Validate refresh token and issue a new access token.

    Raises ValueError on invalid/revoked token.
    """
    try:
        payload = decode_token(refresh_token)
    except JWTError as exc:
        raise ValueError("Invalid refresh token") from exc

    if payload.get("type") != "refresh":
        raise ValueError("Not a refresh token")

    user_id_str: str = payload.get("sub", "")
    jti: str = payload.get("jti", "")

    registered = _refresh_tokens.get(user_id_str, set())
    if jti not in registered:
        raise ValueError("Refresh token has been revoked")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError as exc:
        raise ValueError("Invalid user_id in token") from exc

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise ValueError("User not found")

    # Rotate: revoke old JTI, issue new pair
    registered.discard(jti)
    return issue_tokens(user)


async def logout_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    refresh_token: str,
    ip_address: str | None = None,
) -> None:
    """Revoke the refresh token JTI and write audit log."""
    try:
        payload = decode_token(refresh_token)
        jti: str = payload.get("jti", "")
        user_id_str = str(user_id)
        _refresh_tokens.get(user_id_str, set()).discard(jti)
    except JWTError:
        pass  # Token already invalid — still proceed with audit

    await _write_audit(
        db,
        user_id=user_id,
        operation="logout",
        ip_address=ip_address,
    )
    await db.commit()


# ---------------------------------------------------------------------------
# TOTP / 2FA
# ---------------------------------------------------------------------------

_BACKUP_CODE_LENGTH = 8
_BACKUP_CODE_COUNT = 8
_BACKUP_CODE_ALPHABET = string.ascii_uppercase + string.digits


def _generate_backup_codes() -> list[str]:
    return [
        "".join(secrets.choice(_BACKUP_CODE_ALPHABET) for _ in range(_BACKUP_CODE_LENGTH))
        for _ in range(_BACKUP_CODE_COUNT)
    ]


async def setup_totp(db: AsyncSession, user: User) -> TOTPSetupResponse:
    """Generate a TOTP secret, QR URI, and 8 backup codes.

    Stores the secret on the user record.  Backup code hashes are kept
    in the in-memory store (Phase 1 MVP).
    """
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    qr_uri = totp.provisioning_uri(name=user.username, issuer_name="FEVA")

    plaintext_codes = _generate_backup_codes()
    hashed_codes = [hash_password(code) for code in plaintext_codes]

    user.totp_secret = secret
    user.totp_enabled = True
    _backup_codes[str(user.id)] = hashed_codes

    await db.commit()

    return TOTPSetupResponse(
        secret=secret,
        qr_uri=qr_uri,
        backup_codes=plaintext_codes,
    )


def verify_totp(user: User, code: str) -> bool:
    """Verify a TOTP code or a single-use backup code.

    Returns True if valid.  Consumes the backup code on success.
    """
    if not user.totp_secret:
        return False

    totp = pyotp.TOTP(user.totp_secret)
    if totp.verify(code, valid_window=1):
        return True

    # Check backup codes
    user_id_str = str(user.id)
    stored_hashes = _backup_codes.get(user_id_str, [])
    for i, hashed in enumerate(stored_hashes):
        if verify_password(code, hashed):
            # Consume the backup code (single-use)
            stored_hashes.pop(i)
            return True

    return False
