"""Integration tests for user management API endpoints.

Tests for Task 3.2 from admin-qa-dashboards spec.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_list_users_with_pagination(async_client: AsyncClient, admin_token: str):
    """Test GET /api/v1/admin/users with pagination."""
    response = await async_client.get(
        "/api/v1/admin/users?page=1&page_size=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_create_user_endpoint(async_client: AsyncClient, admin_token: str):
    """Test POST /api/v1/admin/users creates a new user."""
    response = await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "newuser123",
            "email": "newuser123@example.com",
            "password": "StrongPass123",
            "role_id": 2,
            "lga_assignment": ["Lagos"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == "newuser123"


@pytest.mark.asyncio
async def test_create_user_duplicate_username(async_client: AsyncClient, admin_token: str):
    """Test POST /api/v1/admin/users rejects duplicate username."""
    # Create first user
    await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "duplicate_test",
            "email": "first@example.com",
            "password": "StrongPass123",
            "role_id": 2,
        },
    )
    
    # Try to create second user with same username
    response = await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "duplicate_test",
            "email": "second@example.com",
            "password": "StrongPass123",
            "role_id": 2,
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["details"].lower()


@pytest.mark.asyncio
async def test_update_user_endpoint(async_client: AsyncClient, admin_token: str, async_db_session: AsyncSession):
    """Test PATCH /api/v1/admin/users/{user_id} updates user."""
    # Create a user first
    create_response = await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "updatetest",
            "email": "updatetest@example.com",
            "password": "StrongPass123",
            "role_id": 2,
        },
    )
    user_id = create_response.json()["id"]
    
    # Update the user
    response = await async_client.patch(
        f"/api/v1/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "role_id": 3,
            "lga_assignment": ["Abuja"],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_deactivate_user_endpoint(async_client: AsyncClient, admin_token: str):
    """Test DELETE /api/v1/admin/users/{user_id} deactivates user."""
    # Create a user first
    create_response = await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "deletetest",
            "email": "deletetest@example.com",
            "password": "StrongPass123",
            "role_id": 2,
        },
    )
    user_id = create_response.json()["id"]
    
    # Deactivate the user
    response = await async_client.delete(
        f"/api/v1/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "deactivated"


@pytest.mark.asyncio
async def test_reset_password_endpoint(async_client: AsyncClient, admin_token: str):
    """Test POST /api/v1/admin/users/{user_id}/reset-password resets password."""
    # Create a user first
    create_response = await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "resettest",
            "email": "resettest@example.com",
            "password": "StrongPass123",
            "role_id": 2,
        },
    )
    user_id = create_response.json()["id"]
    
    # Reset password
    response = await async_client.post(
        f"/api/v1/admin/users/{user_id}/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "new_password": "NewStrongPass456",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_reset_password_weak_password(async_client: AsyncClient, admin_token: str):
    """Test POST /api/v1/admin/users/{user_id}/reset-password rejects weak password."""
    # Create a user first
    create_response = await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "weakresettest",
            "email": "weakresettest@example.com",
            "password": "StrongPass123",
            "role_id": 2,
        },
    )
    user_id = create_response.json()["id"]
    
    # Try to reset with weak password
    response = await async_client.post(
        f"/api/v1/admin/users/{user_id}/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "new_password": "weak",
        },
    )
    assert response.status_code == 400
    assert "at least 8 characters" in response.json()["details"]


@pytest.mark.asyncio
async def test_user_endpoints_require_admin_role(async_client: AsyncClient):
    """Test that user management endpoints require admin role."""
    # Try to access without authentication
    response = await async_client.get("/api/v1/admin/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_cannot_change_last_admin_role(async_client: AsyncClient, admin_token: str, admin_user: User, async_db_session: AsyncSession):
    """Test that changing the role of the last admin user is prevented.
    
    Validates Requirement 5.5: System SHALL prevent removal of the last Admin_User.
    """
    from sqlalchemy import select
    from app.models.role import Role
    from app.models.user import User
    
    # Get the admin role ID
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    # Count current active admins
    result = await async_db_session.execute(
        select(User)
        .where(User.role_id == admin_role.id)
        .where(User.locked_at.is_(None))
    )
    active_admins = result.scalars().all()
    
    # If there's more than one admin, deactivate all but one (keep the admin_user fixture)
    if len(active_admins) > 1:
        for admin in active_admins:
            if admin.id != admin_user.id:
                await async_client.delete(
                    f"/api/v1/admin/users/{admin.id}",
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
    
    # Refresh the session to get updated admin count
    await async_db_session.commit()
    
    # Now try to change the last admin's role to enumerator (role_id 2)
    response = await async_client.patch(
        f"/api/v1/admin/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "role_id": 2,  # enumerator role
        },
    )
    
    # Should be rejected
    assert response.status_code == 400
    assert "last active admin" in response.json()["details"].lower()


@pytest.mark.asyncio
async def test_cannot_deactivate_last_admin(async_client: AsyncClient, admin_token: str, admin_user: User, async_db_session: AsyncSession):
    """Test that deactivating the last admin user is prevented.
    
    Validates Requirement 5.5: System SHALL prevent removal of the last Admin_User.
    """
    from sqlalchemy import select
    from app.models.role import Role
    from app.models.user import User
    
    # Get the admin role ID
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    # Count current active admins
    result = await async_db_session.execute(
        select(User)
        .where(User.role_id == admin_role.id)
        .where(User.locked_at.is_(None))
    )
    active_admins = result.scalars().all()
    
    # If there's more than one admin, deactivate all but one (keep the admin_user fixture)
    if len(active_admins) > 1:
        for admin in active_admins:
            if admin.id != admin_user.id:
                await async_client.delete(
                    f"/api/v1/admin/users/{admin.id}",
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
    
    # Refresh the session to get updated admin count
    await async_db_session.commit()
    
    # Now try to deactivate the last admin
    response = await async_client.delete(
        f"/api/v1/admin/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    # Should be rejected
    assert response.status_code == 400
    assert "last active admin" in response.json()["details"].lower()


@pytest.mark.asyncio
async def test_can_change_role_when_multiple_admins_exist(async_client: AsyncClient, admin_token: str, async_db_session: AsyncSession):
    """Test that role changes are allowed when multiple admins exist.
    
    Validates that the last admin check only applies when there's truly only one admin.
    """
    from sqlalchemy import select
    from app.models.role import Role
    
    # Get the admin role ID
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    # Create a second admin user
    create_response = await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "secondadmin",
            "email": "secondadmin@example.com",
            "password": "StrongPass123",
            "role_id": admin_role.id,
        },
    )
    assert create_response.status_code == 201
    second_admin_id = create_response.json()["id"]
    
    # Now we should be able to change the second admin's role
    response = await async_client.patch(
        f"/api/v1/admin/users/{second_admin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "role_id": 2,  # enumerator role
        },
    )
    
    # Should succeed
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_can_deactivate_when_multiple_admins_exist(async_client: AsyncClient, admin_token: str, async_db_session: AsyncSession):
    """Test that deactivation is allowed when multiple admins exist.
    
    Validates that the last admin check only applies when there's truly only one admin.
    """
    from sqlalchemy import select
    from app.models.role import Role
    
    # Get the admin role ID
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    # Create a second admin user
    create_response = await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "thirdadmin",
            "email": "thirdadmin@example.com",
            "password": "StrongPass123",
            "role_id": admin_role.id,
        },
    )
    assert create_response.status_code == 201
    third_admin_id = create_response.json()["id"]
    
    # Now we should be able to deactivate the second admin
    response = await async_client.delete(
        f"/api/v1/admin/users/{third_admin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    # Should succeed
    assert response.status_code == 200
    assert response.json()["status"] == "deactivated"

