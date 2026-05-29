"""Tests for password complexity validation and login rate limiting.

Tests for Tasks 2.3, 2.5, and 2.7 from admin-qa-dashboards spec.
"""
import pytest
from datetime import datetime, timedelta, UTC
from httpx import AsyncClient

from app.core.security import validate_password_complexity, hash_password
from app.models.user import User


class TestPasswordComplexity:
    """Test password complexity validation (Task 2.3)."""
    
    def test_valid_password(self):
        """Test that valid passwords pass validation."""
        valid_passwords = [
            "Password1",
            "MyP@ssw0rd",
            "Test1234",
            "Abcdefgh1",
        ]
        for password in valid_passwords:
            is_valid, error = validate_password_complexity(password)
            assert is_valid, f"Password '{password}' should be valid but got error: {error}"
            assert error is None
    
    def test_password_too_short(self):
        """Test that passwords under 8 characters are rejected."""
        is_valid, error = validate_password_complexity("Pass1")
        assert not is_valid
        assert "at least 8 characters" in error
    
    def test_password_no_uppercase(self):
        """Test that passwords without uppercase letters are rejected."""
        is_valid, error = validate_password_complexity("password1")
        assert not is_valid
        assert "uppercase letter" in error
    
    def test_password_no_lowercase(self):
        """Test that passwords without lowercase letters are rejected."""
        is_valid, error = validate_password_complexity("PASSWORD1")
        assert not is_valid
        assert "lowercase letter" in error
    
    def test_password_no_number(self):
        """Test that passwords without numbers are rejected."""
        is_valid, error = validate_password_complexity("Password")
        assert not is_valid
        assert "number" in error
    
    @pytest.mark.asyncio
    async def test_user_creation_with_weak_password(self, async_client: AsyncClient, admin_token: str):
        """Test that user creation rejects weak passwords."""
        response = await async_client.post(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "weak",  # Too short, no uppercase, no number
                "role_id": 2,
                "lga_assignment": None,
            },
        )
        assert response.status_code == 400
        assert "at least 8 characters" in response.json()["details"]
    
    @pytest.mark.asyncio
    async def test_user_creation_with_strong_password(self, async_client: AsyncClient, admin_token: str):
        """Test that user creation accepts strong passwords."""
        response = await async_client.post(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": "stronguser",
                "email": "strong@example.com",
                "password": "StrongPass123",
                "role_id": 2,
                "lga_assignment": None,
            },
        )
        assert response.status_code == 201
        assert "id" in response.json()


class TestLoginRateLimiting:
    """Test login rate limiting (Task 2.5)."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_after_five_attempts(
        self, async_client: AsyncClient, async_db_session
    ):
        """Test that account is locked after 5 failed attempts within 15 minutes."""
        from sqlalchemy import select, text
        from app.models.role import Role
        
        # Get enumerator role
        result = await async_db_session.execute(
            select(Role).where(Role.name == "enumerator")
        )
        role = result.scalar_one_or_none()
        if not role:
            role = Role(id=2, name="enumerator")
            async_db_session.add(role)
            await async_db_session.flush()
        
        # Create a test user
        user = User(
            username="ratelimituser",
            email="ratelimit@example.com",
            password_hash=hash_password("CorrectPass1"),
            role_id=role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        
        # Attempt 5 failed logins
        for i in range(5):
            response = await async_client.post(
                "/api/v1/auth/login",
                json={"username": "ratelimituser", "password": "WrongPass1"},
            )
            if i < 4:
                assert response.status_code == 401, f"Attempt {i+1} should return 401"
            else:
                # 5th attempt should trigger rate limit
                assert response.status_code == 429, "5th attempt should return 429"
                assert "Too many failed login attempts" in response.json()["details"]
        
        # Verify subsequent login attempts are blocked
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "ratelimituser", "password": "CorrectPass1"},
        )
        assert response.status_code == 429
    
    @pytest.mark.asyncio
    async def test_rate_limit_window_reset(
        self, async_client: AsyncClient, async_db_session
    ):
        """Test that rate limit window resets after 15 minutes."""
        from sqlalchemy import select, text
        from app.models.role import Role
        
        # Get enumerator role
        result = await async_db_session.execute(
            select(Role).where(Role.name == "enumerator")
        )
        role = result.scalar_one_or_none()
        if not role:
            role = Role(id=2, name="enumerator")
            async_db_session.add(role)
            await async_db_session.flush()
        
        # Create a test user
        user = User(
            username="windowresetuser",
            email="windowreset@example.com",
            password_hash=hash_password("CorrectPass1"),
            role_id=role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        
        # Simulate 3 failed attempts
        for i in range(3):
            response = await async_client.post(
                "/api/v1/auth/login",
                json={"username": "windowresetuser", "password": "WrongPass1"},
            )
            assert response.status_code == 401
        
        # Manually set the window start to 16 minutes ago
        window_time = (datetime.now(UTC) - timedelta(minutes=16)).isoformat()
        await async_db_session.execute(
            text(
                "UPDATE users SET failed_attempts_window_start = :window_time "
                "WHERE username = :username"
            ),
            {"window_time": window_time, "username": "windowresetuser"}
        )
        await async_db_session.commit()
        
        # Next failed attempt should reset the window
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "windowresetuser", "password": "WrongPass1"},
        )
        assert response.status_code == 401  # Not locked yet
        
        # Verify the counter was reset (should be able to fail 4 more times)
        for i in range(4):
            response = await async_client.post(
                "/api/v1/auth/login",
                json={"username": "windowresetuser", "password": "WrongPass1"},
            )
            if i < 3:
                assert response.status_code == 401
            else:
                assert response.status_code == 429  # Locked on 5th attempt
    
    @pytest.mark.asyncio
    async def test_successful_login_resets_counter(
        self, async_client: AsyncClient, async_db_session
    ):
        """Test that successful login resets failed attempts counter."""
        from sqlalchemy import select
        from app.models.role import Role
        
        # Get enumerator role
        result = await async_db_session.execute(
            select(Role).where(Role.name == "enumerator")
        )
        role = result.scalar_one_or_none()
        if not role:
            role = Role(id=2, name="enumerator")
            async_db_session.add(role)
            await async_db_session.flush()
        
        # Create a test user
        user = User(
            username="resetcounteruser",
            email="resetcounter@example.com",
            password_hash=hash_password("CorrectPass1"),
            role_id=role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        
        # Fail 3 times
        for i in range(3):
            response = await async_client.post(
                "/api/v1/auth/login",
                json={"username": "resetcounteruser", "password": "WrongPass1"},
            )
            assert response.status_code == 401
        
        # Successful login
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "resetcounteruser", "password": "CorrectPass1"},
        )
        assert response.status_code == 200
        
        # Verify counter was reset - should be able to fail 5 more times
        for i in range(5):
            response = await async_client.post(
                "/api/v1/auth/login",
                json={"username": "resetcounteruser", "password": "WrongPass1"},
            )
            if i < 4:
                assert response.status_code == 401
            else:
                assert response.status_code == 429


class TestPostLoginRedirect:
    """Test post-login redirect based on role (Task 2.7)."""
    
    @pytest.mark.asyncio
    async def test_admin_login_returns_admin_role(
        self, async_client: AsyncClient, async_db_session
    ):
        """Test that admin login returns role='admin' for frontend redirect."""
        from sqlalchemy import select
        from app.models.role import Role
        
        # Get admin role
        result = await async_db_session.execute(
            select(Role).where(Role.name == "admin")
        )
        role = result.scalar_one_or_none()
        if not role:
            role = Role(id=1, name="admin")
            async_db_session.add(role)
            await async_db_session.flush()
        
        # Create admin user
        user = User(
            username="adminuser",
            email="admin@example.com",
            password_hash=hash_password("AdminPass1"),
            role_id=role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "adminuser", "password": "AdminPass1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"
        assert "access_token" in data
    
    @pytest.mark.asyncio
    async def test_qa_officer_login_returns_qa_role(
        self, async_client: AsyncClient, async_db_session
    ):
        """Test that QA officer login returns role='qa_officer' for frontend redirect."""
        from sqlalchemy import select
        from app.models.role import Role
        
        # Get QA officer role
        result = await async_db_session.execute(
            select(Role).where(Role.name == "qa_officer")
        )
        role = result.scalar_one_or_none()
        if not role:
            role = Role(id=4, name="qa_officer")
            async_db_session.add(role)
            await async_db_session.flush()
        
        # Create QA officer user
        user = User(
            username="qauser",
            email="qa@example.com",
            password_hash=hash_password("QaPass123"),
            role_id=role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "qauser", "password": "QaPass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "qa_officer"
        assert "access_token" in data
    
    @pytest.mark.asyncio
    async def test_enumerator_login_returns_enumerator_role(
        self, async_client: AsyncClient, async_db_session
    ):
        """Test that enumerator login returns role='enumerator' for frontend redirect."""
        from sqlalchemy import select
        from app.models.role import Role
        
        # Get enumerator role
        result = await async_db_session.execute(
            select(Role).where(Role.name == "enumerator")
        )
        role = result.scalar_one_or_none()
        if not role:
            role = Role(id=2, name="enumerator")
            async_db_session.add(role)
            await async_db_session.flush()
        
        # Create enumerator user
        user = User(
            username="enumuser",
            email="enum@example.com",
            password_hash=hash_password("EnumPass1"),
            role_id=role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "enumuser", "password": "EnumPass1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "enumerator"
        assert "access_token" in data


