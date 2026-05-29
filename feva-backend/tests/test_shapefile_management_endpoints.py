"""Tests for shapefile management endpoints.

Tests the GET /api/v1/admin/shapefiles and PATCH /api/v1/admin/shapefiles/{id}/activate
endpoints for listing and activating shapefile versions.

Requirements: 7.4, 7.5, 18.4, 18.7
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shapefile_version import ShapefileVersion
from app.models.user import User


@pytest.mark.asyncio
async def test_list_shapefiles_requires_admin_role(client: AsyncClient, async_db_session: AsyncSession):
    """GET /api/v1/admin/shapefiles requires admin role."""
    from app.core.security import hash_password, create_access_token
    from app.models.role import Role
    
    result = await async_db_session.execute(select(Role).where(Role.name == "enumerator"))
    enumerator_role = result.scalar_one()
    
    user = User(
        username="enumerator_user",
        email="enumerator@test.com",
        password_hash=hash_password("Test1234"),
        role_id=enumerator_role.id,
    )
    async_db_session.add(user)
    await async_db_session.commit()
    
    token = create_access_token({"sub": str(user.id), "role": "enumerator"})
    
    response = await client.get(
        "/api/v1/admin/shapefiles",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_shapefiles_returns_empty_list(client: AsyncClient, async_db_session: AsyncSession):
    """GET /api/v1/admin/shapefiles returns empty list when no shapefiles exist."""
    from app.core.security import hash_password, create_access_token
    from app.models.role import Role
    
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    admin = User(
        username="admin_test",
        email="admin@test.com",
        password_hash=hash_password("Test1234"),
        role_id=admin_role.id,
    )
    async_db_session.add(admin)
    await async_db_session.commit()
    
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    
    response = await client.get(
        "/api/v1/admin/shapefiles",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_shapefiles_returns_all_versions(client: AsyncClient, async_db_session: AsyncSession):
    """GET /api/v1/admin/shapefiles returns all shapefile versions with metadata."""
    from app.core.security import hash_password, create_access_token
    from app.models.role import Role
    
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    admin = User(
        username="admin_list",
        email="admin_list@test.com",
        password_hash=hash_password("Test1234"),
        role_id=admin_role.id,
    )
    async_db_session.add(admin)
    await async_db_session.flush()
    
    version1 = ShapefileVersion(
        layer_name="lga",
        version_tag="2024-Q1",
        checksum_sha256="abc123",
        uploaded_by=admin.id,
        is_active=False,
    )
    version2 = ShapefileVersion(
        layer_name="lga",
        version_tag="2024-Q2",
        checksum_sha256="def456",
        uploaded_by=admin.id,
        is_active=True,
    )
    version3 = ShapefileVersion(
        layer_name="ward",
        version_tag="2024-Q1",
        checksum_sha256="ghi789",
        uploaded_by=admin.id,
        is_active=True,
    )
    async_db_session.add_all([version1, version2, version3])
    await async_db_session.commit()
    
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    
    response = await client.get(
        "/api/v1/admin/shapefiles",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    
    for item in data:
        assert "id" in item
        assert "layer_name" in item
        assert "version_tag" in item
        assert "checksum_sha256" in item
        assert "uploaded_by" in item
        assert "uploaded_at" in item
        assert "is_active" in item
    
    assert data[0]["layer_name"] == "ward"
    assert data[0]["version_tag"] == "2024-Q1"


@pytest.mark.asyncio
async def test_activate_shapefile_requires_admin_role(client: AsyncClient, async_db_session: AsyncSession):
    """PATCH /api/v1/admin/shapefiles/{id}/activate requires admin role."""
    from app.core.security import hash_password, create_access_token
    from app.models.role import Role
    
    result = await async_db_session.execute(select(Role).where(Role.name == "enumerator"))
    enumerator_role = result.scalar_one()
    
    user = User(
        username="enumerator_activate",
        email="enumerator_activate@test.com",
        password_hash=hash_password("Test1234"),
        role_id=enumerator_role.id,
    )
    async_db_session.add(user)
    await async_db_session.commit()
    
    token = create_access_token({"sub": str(user.id), "role": "enumerator"})
    
    response = await client.patch(
        "/api/v1/admin/shapefiles/1/activate",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_activate_shapefile_returns_404_for_invalid_id(client: AsyncClient, async_db_session: AsyncSession):
    """PATCH /api/v1/admin/shapefiles/{id}/activate returns 404 for non-existent ID."""
    from app.core.security import hash_password, create_access_token
    from app.models.role import Role
    
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    admin = User(
        username="admin_404",
        email="admin_404@test.com",
        password_hash=hash_password("Test1234"),
        role_id=admin_role.id,
    )
    async_db_session.add(admin)
    await async_db_session.commit()
    
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    
    response = await client.patch(
        "/api/v1/admin/shapefiles/99999/activate",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_activate_shapefile_marks_version_as_active(client: AsyncClient, async_db_session: AsyncSession):
    """PATCH /api/v1/admin/shapefiles/{id}/activate marks the version as active."""
    from app.core.security import hash_password, create_access_token
    from app.models.role import Role
    
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    admin = User(
        username="admin_activate",
        email="admin_activate@test.com",
        password_hash=hash_password("Test1234"),
        role_id=admin_role.id,
    )
    async_db_session.add(admin)
    await async_db_session.flush()
    
    version1 = ShapefileVersion(
        layer_name="lga",
        version_tag="2024-Q1",
        checksum_sha256="abc123",
        uploaded_by=admin.id,
        is_active=True,
    )
    version2 = ShapefileVersion(
        layer_name="lga",
        version_tag="2024-Q2",
        checksum_sha256="def456",
        uploaded_by=admin.id,
        is_active=False,
    )
    async_db_session.add_all([version1, version2])
    await async_db_session.commit()
    
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    
    response = await client.patch(
        f"/api/v1/admin/shapefiles/{version2.id}/activate",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "activated"
    
    await async_db_session.refresh(version1)
    await async_db_session.refresh(version2)
    
    assert version2.is_active is True
    assert version1.is_active is False


@pytest.mark.asyncio
async def test_activate_shapefile_deactivates_other_versions_same_layer(
    client: AsyncClient, async_db_session: AsyncSession
):
    """PATCH /api/v1/admin/shapefiles/{id}/activate deactivates other versions of the same layer."""
    from app.core.security import hash_password, create_access_token
    from app.models.role import Role
    
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    admin = User(
        username="admin_deactivate",
        email="admin_deactivate@test.com",
        password_hash=hash_password("Test1234"),
        role_id=admin_role.id,
    )
    async_db_session.add(admin)
    await async_db_session.flush()
    
    version1 = ShapefileVersion(
        layer_name="lga",
        version_tag="2024-Q1",
        checksum_sha256="abc123",
        uploaded_by=admin.id,
        is_active=True,
    )
    version2 = ShapefileVersion(
        layer_name="lga",
        version_tag="2024-Q2",
        checksum_sha256="def456",
        uploaded_by=admin.id,
        is_active=False,
    )
    version3 = ShapefileVersion(
        layer_name="lga",
        version_tag="2024-Q3",
        checksum_sha256="ghi789",
        uploaded_by=admin.id,
        is_active=False,
    )
    version4 = ShapefileVersion(
        layer_name="ward",
        version_tag="2024-Q1",
        checksum_sha256="jkl012",
        uploaded_by=admin.id,
        is_active=True,
    )
    async_db_session.add_all([version1, version2, version3, version4])
    await async_db_session.commit()
    
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    
    response = await client.patch(
        f"/api/v1/admin/shapefiles/{version3.id}/activate",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    
    await async_db_session.refresh(version1)
    await async_db_session.refresh(version2)
    await async_db_session.refresh(version3)
    await async_db_session.refresh(version4)
    
    assert version1.is_active is False
    assert version2.is_active is False
    assert version3.is_active is True
    assert version4.is_active is True


@pytest.mark.asyncio
async def test_activate_shapefile_creates_audit_log(client: AsyncClient, async_db_session: AsyncSession):
    """PATCH /api/v1/admin/shapefiles/{id}/activate creates an audit log entry."""
    from app.core.security import hash_password, create_access_token
    from app.models.role import Role
    from app.models.audit_log import AuditLog
    
    result = await async_db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()
    
    admin = User(
        username="admin_audit",
        email="admin_audit@test.com",
        password_hash=hash_password("Test1234"),
        role_id=admin_role.id,
    )
    async_db_session.add(admin)
    await async_db_session.flush()
    
    version = ShapefileVersion(
        layer_name="lga",
        version_tag="2024-Q1",
        checksum_sha256="abc123",
        uploaded_by=admin.id,
        is_active=False,
    )
    async_db_session.add(version)
    await async_db_session.commit()
    
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    
    response = await client.patch(
        f"/api/v1/admin/shapefiles/{version.id}/activate",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    
    result = await async_db_session.execute(
        select(AuditLog)
        .where(AuditLog.operation == "activate_shapefile")
        .where(AuditLog.entity_id == str(version.id))
    )
    audit_entry = result.scalar_one_or_none()
    
    assert audit_entry is not None
    assert audit_entry.user_id == admin.id
    assert audit_entry.entity_type == "shapefile_version"
    assert audit_entry.detail["layer_name"] == "lga"
    assert audit_entry.detail["version_tag"] == "2024-Q1"
