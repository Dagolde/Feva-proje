"""JWT Token Management Tests for Admin QA Dashboards.

Tests JWT token creation with role claims and 8-hour expiration.

Task: 1.1 - Implement JWT token management with role claims
Requirements: 3.2, 3.4
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_token,
    hash_password,
)
from app.services.auth_service import issue_tokens


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_user(
    *,
    username: str = "testuser",
    role_name: str = "admin",
) -> MagicMock:
    """Return a mock User ORM object with role."""
    user = MagicMock()
    user.id = uuid.uuid4()
    user.username = username
    user.password_hash = hash_password("test-password")
    user.role = MagicMock()
    user.role.name = role_name
    return user


# ── Test 1: Token includes role claim ─────────────────────────────────────────

def test_token_includes_role_claim():
    """JWT token payload must include the user's role.
    
    Validates: Requirement 3.2 - JWT_Token SHALL include user role information
    """
    user = _make_user(role_name="admin")
    
    tokens = issue_tokens(user)
    
    # Decode the access token
    payload = decode_token(tokens.access_token)
    
    # Verify role is in the payload
    assert "role" in payload
    assert payload["role"] == "admin"
    
    # Verify other required claims
    assert "sub" in payload
    assert payload["sub"] == str(user.id)
    assert "jti" in payload
    assert "exp" in payload
    assert "iat" in payload


def test_token_includes_role_for_qa_officer():
    """JWT token includes role for QA officer users."""
    user = _make_user(role_name="qa_officer")
    
    tokens = issue_tokens(user)
    payload = decode_token(tokens.access_token)
    
    assert payload["role"] == "qa_officer"


def test_token_includes_role_for_enumerator():
    """JWT token includes role for enumerator users."""
    user = _make_user(role_name="enumerator")
    
    tokens = issue_tokens(user)
    payload = decode_token(tokens.access_token)
    
    assert payload["role"] == "enumerator"


def test_token_includes_role_for_supervisor():
    """JWT token includes role for supervisor users."""
    user = _make_user(role_name="supervisor")
    
    tokens = issue_tokens(user)
    payload = decode_token(tokens.access_token)
    
    assert payload["role"] == "supervisor"


# ── Test 2: Token expires after 8 hours ───────────────────────────────────────

def test_token_expires_after_8_hours():
    """JWT token expiration must be set to 8 hours from creation.
    
    Validates: Requirement 3.4 - JWT_Token SHALL expire after 8 hours
    """
    user = _make_user()
    
    before_creation = datetime.now(UTC)
    tokens = issue_tokens(user)
    after_creation = datetime.now(UTC)
    
    # Decode the token
    payload = decode_token(tokens.access_token)
    
    # Get expiration timestamp
    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=UTC)
    
    # Calculate expected expiration (8 hours from now)
    expected_exp_min = before_creation + timedelta(hours=8)
    expected_exp_max = after_creation + timedelta(hours=8)
    
    # Verify expiration is approximately 8 hours from now
    # Allow 2 second tolerance for test execution time and timestamp precision
    assert expected_exp_min - timedelta(seconds=1) <= exp_datetime <= expected_exp_max + timedelta(seconds=2)


def test_token_expiration_claim_format():
    """Token expiration claim must be a valid Unix timestamp."""
    user = _make_user()
    tokens = issue_tokens(user)
    payload = decode_token(tokens.access_token)
    
    # exp should be an integer timestamp
    assert isinstance(payload["exp"], int)
    
    # exp should be in the future
    now = datetime.now(UTC).timestamp()
    assert payload["exp"] > now


def test_token_expires_in_field():
    """TokenResponse expires_in field should reflect 8 hours in seconds."""
    user = _make_user()
    tokens = issue_tokens(user)
    
    # 8 hours = 28800 seconds
    expected_seconds = 8 * 60 * 60
    assert tokens.expires_in == expected_seconds


# ── Test 3: Token validation and decoding ─────────────────────────────────────

def test_valid_token_can_be_decoded():
    """Valid JWT tokens can be decoded successfully."""
    user_id = uuid.uuid4()
    token_data = {
        "sub": str(user_id),
        "role": "admin",
        "jti": str(uuid.uuid4()),
    }
    
    token = create_access_token(token_data)
    payload = decode_token(token)
    
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "admin"


def test_expired_token_raises_error():
    """Expired tokens should raise an error when decoded."""
    from jose import JWTError
    
    user_id = uuid.uuid4()
    token_data = {
        "sub": str(user_id),
        "role": "admin",
    }
    
    # Create token that expires immediately
    expired_token = create_access_token(
        token_data,
        expires_delta=timedelta(seconds=-1)
    )
    
    # Attempting to decode should raise JWTError
    with pytest.raises(JWTError):
        decode_token(expired_token)


def test_malformed_token_raises_error():
    """Malformed tokens should raise an error when decoded."""
    from jose import JWTError
    
    malformed_token = "not.a.valid.jwt.token"
    
    with pytest.raises(JWTError):
        decode_token(malformed_token)


def test_token_with_invalid_signature_raises_error():
    """Tokens with invalid signatures should be rejected."""
    from jose import JWTError
    
    user_id = uuid.uuid4()
    token_data = {
        "sub": str(user_id),
        "role": "admin",
    }
    
    # Create a token
    token = create_access_token(token_data)
    
    # Tamper with the token by completely replacing the signature
    parts = token.split(".")
    if len(parts) == 3:
        # Replace signature with invalid base64
        parts[2] = "invalid_signature_that_will_fail_verification"
        tampered_token = ".".join(parts)
        
        # Attempting to decode should raise JWTError
        with pytest.raises(JWTError):
            decode_token(tampered_token)


# ── Test 4: Token includes issued-at claim ────────────────────────────────────

def test_token_includes_iat_claim():
    """JWT token should include issued-at (iat) timestamp."""
    user = _make_user()
    
    before_creation = int(datetime.now(UTC).timestamp())
    tokens = issue_tokens(user)
    after_creation = int(datetime.now(UTC).timestamp())
    
    payload = decode_token(tokens.access_token)
    
    # Verify iat claim exists
    assert "iat" in payload
    assert isinstance(payload["iat"], int)
    
    # Verify iat is approximately now (allow 2 second tolerance)
    assert before_creation - 1 <= payload["iat"] <= after_creation + 2


# ── Test 5: Refresh token also includes role ──────────────────────────────────

def test_refresh_token_includes_role():
    """Refresh tokens should also include role information."""
    user = _make_user(role_name="qa_officer")
    
    tokens = issue_tokens(user)
    
    # Decode the refresh token
    payload = decode_token(tokens.refresh_token)
    
    # Verify role is in the refresh token payload
    assert "role" in payload
    assert payload["role"] == "qa_officer"
    assert payload["type"] == "refresh"


# ── Test 6: TokenResponse includes role field ─────────────────────────────────

def test_token_response_includes_role_field():
    """TokenResponse object should include the role field."""
    user = _make_user(role_name="admin")
    
    tokens = issue_tokens(user)
    
    # Verify TokenResponse has role field
    assert hasattr(tokens, "role")
    assert tokens.role == "admin"


def test_token_response_includes_user_id():
    """TokenResponse object should include the user_id field."""
    user = _make_user()
    
    tokens = issue_tokens(user)
    
    # Verify TokenResponse has user_id field
    assert hasattr(tokens, "user_id")
    assert tokens.user_id == str(user.id)


# ── Test 7: Multiple roles produce different tokens ───────────────────────────

def test_different_roles_produce_different_tokens():
    """Tokens for different roles should have different role claims."""
    admin_user = _make_user(username="admin", role_name="admin")
    qa_user = _make_user(username="qa", role_name="qa_officer")
    
    admin_tokens = issue_tokens(admin_user)
    qa_tokens = issue_tokens(qa_user)
    
    admin_payload = decode_token(admin_tokens.access_token)
    qa_payload = decode_token(qa_tokens.access_token)
    
    assert admin_payload["role"] == "admin"
    assert qa_payload["role"] == "qa_officer"
    assert admin_payload["role"] != qa_payload["role"]
