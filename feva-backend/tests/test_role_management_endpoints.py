"""Tests for role management endpoints.

Tests the GET /api/v1/admin/roles endpoint that lists all roles with permissions.

Requirements: 5.1, 5.2, 5.3, 18.2, 18.7
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.core.security import create_access_token


@pytest.mark.asyncio
class TestRoleManagementEndpoints:
    """Test suite for role management API endpoints."""

    async def test_list_roles_requires_admin_role(
        self, async_client: AsyncClient, enumerator_user
    ):
        """Test that listing roles requires admin role.
        
        Requirements: 18.7
        """
        # Create token for a non-admin user (enumerator)
        token = create_access_token({"sub": str(enumerator_user.id), "role": "enumerator"})

        # Try to access roles endpoint
        response = await async_client.get(
            "/api/v1/admin/roles",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["details"]

    async def test_list_roles_returns_all_roles_with_permissions(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that listing roles returns all roles with their permissions.
        
        Requirements: 5.1, 5.2, 5.3, 18.2
        """
        # Create token for admin
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        # Get roles
        response = await async_client.get(
            "/api/v1/admin/roles",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        roles = response.json()
        
        # Verify we got at least the admin role
        assert len(roles) >= 1
        role_names_returned = {role["name"] for role in roles}
        assert "admin" in role_names_returned
        
        # Verify each role has permissions
        for role in roles:
            assert "id" in role
            assert "name" in role
            assert "permissions" in role
            assert isinstance(role["permissions"], list)
            assert len(role["permissions"]) > 0

    async def test_admin_role_has_expected_permissions(
        self, async_client: AsyncClient, admin_user
    ):
        """Test that admin role has all expected permissions.
        
        Requirements: 5.3
        """
        # Create token for admin
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        # Get roles
        response = await async_client.get(
            "/api/v1/admin/roles",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        roles = response.json()
        
        # Find admin role
        admin_role_data = next((r for r in roles if r["name"] == "admin"), None)
        assert admin_role_data is not None
        
        # Verify admin has comprehensive permissions
        expected_permissions = {
            "manage_users",
            "manage_roles",
            "manage_system_config",
            "manage_shapefiles",
            "export_data",
            "view_audit_logs",
            "view_monitoring",
            "review_records",
            "manage_dropdown_config",
        }
        actual_permissions = set(admin_role_data["permissions"])
        assert actual_permissions == expected_permissions

    async def test_qa_officer_role_has_review_permissions(
        self, async_client: AsyncClient, admin_user, async_db_session: AsyncSession
    ):
        """Test that qa_officer role has review-related permissions.
        
        Requirements: 5.3
        """
        from sqlalchemy import select
        
        # Ensure qa_officer role exists
        result = await async_db_session.execute(
            select(Role).where(Role.name == "qa_officer")
        )
        qa_role = result.scalar_one_or_none()
        if not qa_role:
            qa_role = Role(id=4, name="qa_officer")
            async_db_session.add(qa_role)
            await async_db_session.commit()
        
        # Create token for admin
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        # Get roles
        response = await async_client.get(
            "/api/v1/admin/roles",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        roles = response.json()
        
        # Find qa_officer role
        qa_role_data = next((r for r in roles if r["name"] == "qa_officer"), None)
        assert qa_role_data is not None
        
        # Verify QA officer has review permissions
        expected_permissions = {
            "review_records",
            "approve_records",
            "reject_records",
            "view_qa_statistics",
            "view_audit_trail",
        }
        actual_permissions = set(qa_role_data["permissions"])
        assert actual_permissions == expected_permissions

    async def test_enumerator_role_has_limited_permissions(
        self, async_client: AsyncClient, admin_user, async_db_session: AsyncSession
    ):
        """Test that enumerator role has limited field permissions.
        
        Requirements: 5.3
        """
        from sqlalchemy import select
        
        # Ensure enumerator role exists
        result = await async_db_session.execute(
            select(Role).where(Role.name == "enumerator")
        )
        enum_role = result.scalar_one_or_none()
        if not enum_role:
            enum_role = Role(id=2, name="enumerator")
            async_db_session.add(enum_role)
            await async_db_session.commit()
        
        # Create token for admin
        token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
        
        # Get roles
        response = await async_client.get(
            "/api/v1/admin/roles",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        roles = response.json()
        
        # Find enumerator role
        enum_role_data = next((r for r in roles if r["name"] == "enumerator"), None)
        assert enum_role_data is not None
        
        # Verify enumerator has limited permissions
        expected_permissions = {
            "create_records",
            "edit_own_records",
            "upload_photos",
            "sync_data",
        }
        actual_permissions = set(enum_role_data["permissions"])
        assert actual_permissions == expected_permissions
        
        # Verify enumerator does NOT have admin permissions
        assert "manage_users" not in actual_permissions
        assert "manage_roles" not in actual_permissions
        assert "export_data" not in actual_permissions

    async def test_unauthenticated_access_returns_401(
        self, async_client: AsyncClient
    ):
        """Test that unauthenticated access to roles endpoint returns 401.
        
        Requirements: 18.7
        """
        response = await async_client.get("/api/v1/admin/roles")
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["details"]

