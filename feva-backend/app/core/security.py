"""JWT RS256 utilities and password hashing."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_password_complexity(password: str) -> tuple[bool, str | None]:
    """Validate password complexity requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    
    Returns:
        tuple[bool, str | None]: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, None


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# RSA key management
# ---------------------------------------------------------------------------

def _load_or_generate_keys() -> tuple[str, str]:
    """Return (private_key_pem, public_key_pem).

    Uses configured PEM keys when available; otherwise generates an ephemeral
    RSA-2048 pair (acceptable for dev/test only).
    """
    if settings.JWT_PRIVATE_KEY and settings.JWT_PUBLIC_KEY:
        return settings.JWT_PRIVATE_KEY, settings.JWT_PUBLIC_KEY

    # Ephemeral key generation — dev/test only
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


_PRIVATE_KEY, _PUBLIC_KEY = _load_or_generate_keys()

# ---------------------------------------------------------------------------
# Token creation / decoding
# ---------------------------------------------------------------------------

ALGORITHM = "RS256"


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {**data, "exp": expire, "iat": datetime.now(UTC), "type": "access"}
    return jwt.encode(payload, _PRIVATE_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {**data, "exp": expire, "iat": datetime.now(UTC), "type": "refresh"}
    return jwt.encode(payload, _PRIVATE_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify an RS256 JWT.  Raises JWTError on failure."""
    return jwt.decode(token, _PUBLIC_KEY, algorithms=[ALGORITHM])  # type: ignore[return-value]


__all__ = [
    "hash_password",
    "verify_password",
    "validate_password_complexity",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "ALGORITHM",
]
