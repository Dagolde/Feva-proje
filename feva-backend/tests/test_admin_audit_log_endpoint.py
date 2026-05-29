"""Tests for admin audit log query endpoint.

Tests Task 8.2: Create audit log query endpoint at `/api/v1/admin/audit-log`
- GET `/api/v1/admin/audit-log` - Query audit logs with pagination
- Support filters for user_id, operation, entity_type, date range
- Return audit entries with timestamp, user, operation, entity details
- Require admin role
- Requirements: 18.7
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User


@pytest.fixture
async def test_enumerator(async_db_session):
    """Get or create an enumerator user for testing."""
    from app.models.role import Role
    from app.core.security import hash_password
    from sqlalchemy import select
    
    # Get or create enumerator role
    result = await async_db_session.execute(select(Role).where(Role.name == "enumerator"))
    enum_role = result.scalar_one_or_none()
    
    if not enum_role:
        enum_role = Role(id=2, name="enumerator")
        async_db_session.add(enum_role)
        await async_db_session.flush()
    
    # Get or create enumerator user
    result = await async_db_session.execute(select(User).where(User.username == "test_enumerator"))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            username="test_enumerator",
            email="enumerator@test.com",
            password_hash=hash_password("testpass123"),
            role_id=enum_role.id,
        )
        async_db_session.add(user)
        await async_db_session.commit()
        await async_db_session.refresh(user)
    else:
        await async_db_session.refresh(user)
    
    return user


@pytest.fixture
def enumerator_token(test_enumerator):
    """Generate an access token for the enumerator user."""
    from app.core.security import create_access_token
    
    return create_access_token(
        {"sub": str(test_enumerator.id), "role": "enumerator"}
    )


@pytest.mark.asyncio
async def test_audit_log_requires_admin_role(
    client: AsyncClient,
    test_enumerator: User,
    enumerator_token: str,
):
    """Test that audit log endpoint requires admin role."""
    response = await client.get(
        "/api/v1/admin/audit-log",
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_audit_log_basic_pagination(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test basic audit log retrieval with pagination."""
    # Create some audit log entries
    for i in range(5):
        audit = AuditLog(
            user_id=admin_user.id,
            operation=f"test_operation_{i}",
            entity_type="test_entity",
            entity_id=str(uuid.uuid4()),
            detail={"test": f"data_{i}"},
        )
        async_db_session.add(audit)
    await async_db_session.commit()
    
    # Query audit logs
    response = await client.get(
        "/api/v1/admin/audit-log?page=1&page_size=3",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "items" in data
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["items"]) <= 3


@pytest.mark.asyncio
async def test_audit_log_ordered_by_timestamp_descending(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test that audit logs are ordered by occurred_at descending (newest first)."""
    # Create audit log entries with different timestamps
    now = datetime.now(timezone.utc)
    
    audit1 = AuditLog(
        user_id=admin_user.id,
        operation="first_operation",
        entity_type="test",
        entity_id="1",
    )
    async_db_session.add(audit1)
    await async_db_session.flush()
    
    # Manually set timestamp to ensure ordering
    audit1.occurred_at = now - timedelta(hours=2)
    
    audit2 = AuditLog(
        user_id=admin_user.id,
        operation="second_operation",
        entity_type="test",
        entity_id="2",
    )
    async_db_session.add(audit2)
    await async_db_session.flush()
    
    audit2.occurred_at = now - timedelta(hours=1)
    
    audit3 = AuditLog(
        user_id=admin_user.id,
        operation="third_operation",
        entity_type="test",
        entity_id="3",
    )
    async_db_session.add(audit3)
    await async_db_session.flush()
    
    audit3.occurred_at = now
    
    await async_db_session.commit()
    
    # Query audit logs
    response = await client.get(
        "/api/v1/admin/audit-log?page_size=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Find our test operations
    test_items = [
        item for item in data["items"]
        if item["operation"] in ["first_operation", "second_operation", "third_operation"]
    ]
    
    # Should be ordered newest first
    assert len(test_items) >= 3
    operations = [item["operation"] for item in test_items[:3]]
    assert operations[0] == "third_operation"
    assert operations[1] == "second_operation"
    assert operations[2] == "first_operation"


@pytest.mark.asyncio
async def test_audit_log_filter_by_user_id(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    test_enumerator: User,
    admin_token: str,
):
    """Test filtering audit logs by user_id."""
    # Create audit logs for different users
    audit_admin = AuditLog(
        user_id=admin_user.id,
        operation="admin_operation",
        entity_type="test",
        entity_id="1",
    )
    async_db_session.add(audit_admin)
    
    audit_enum = AuditLog(
        user_id=test_enumerator.id,
        operation="enumerator_operation",
        entity_type="test",
        entity_id="2",
    )
    async_db_session.add(audit_enum)
    await async_db_session.commit()
    
    # Query audit logs filtered by enumerator user_id
    response = await client.get(
        f"/api/v1/admin/audit-log?user_id={test_enumerator.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # All returned items should be for the enumerator
    for item in data["items"]:
        if item["user"]:
            assert item["user"]["id"] == str(test_enumerator.id)


@pytest.mark.asyncio
async def test_audit_log_filter_by_operation(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test filtering audit logs by operation type."""
    # Create audit logs with different operations
    audit1 = AuditLog(
        user_id=admin_user.id,
        operation="create_user",
        entity_type="user",
        entity_id="1",
    )
    async_db_session.add(audit1)
    
    audit2 = AuditLog(
        user_id=admin_user.id,
        operation="update_dropdown",
        entity_type="dropdown_config",
        entity_id="2",
    )
    async_db_session.add(audit2)
    await async_db_session.commit()
    
    # Query audit logs filtered by operation
    response = await client.get(
        "/api/v1/admin/audit-log?operation=create_user",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # All returned items should have the specified operation
    for item in data["items"]:
        if item["operation"] == "create_user":
            assert item["entity_type"] == "user"


@pytest.mark.asyncio
async def test_audit_log_filter_by_entity_type(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test filtering audit logs by entity_type."""
    # Create audit logs with different entity types
    audit1 = AuditLog(
        user_id=admin_user.id,
        operation="create",
        entity_type="user",
        entity_id="1",
    )
    async_db_session.add(audit1)
    
    audit2 = AuditLog(
        user_id=admin_user.id,
        operation="update",
        entity_type="dropdown_config",
        entity_id="2",
    )
    async_db_session.add(audit2)
    await async_db_session.commit()
    
    # Query audit logs filtered by entity_type
    response = await client.get(
        "/api/v1/admin/audit-log?entity_type=dropdown_config",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # All returned items should have the specified entity_type
    for item in data["items"]:
        if item["entity_type"] == "dropdown_config":
            assert item["operation"] == "update"


@pytest.mark.asyncio
async def test_audit_log_filter_by_date_range(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test filtering audit logs by date range."""
    now = datetime.now(timezone.utc)
    
    # Create audit logs with different timestamps
    audit_old = AuditLog(
        user_id=admin_user.id,
        operation="old_operation",
        entity_type="test",
        entity_id="1",
    )
    async_db_session.add(audit_old)
    await async_db_session.flush()
    audit_old.occurred_at = now - timedelta(days=10)
    
    audit_recent = AuditLog(
        user_id=admin_user.id,
        operation="recent_operation",
        entity_type="test",
        entity_id="2",
    )
    async_db_session.add(audit_recent)
    await async_db_session.flush()
    audit_recent.occurred_at = now - timedelta(days=2)
    
    await async_db_session.commit()
    
    # Query audit logs with date range (last 5 days)
    date_from = (now - timedelta(days=5)).isoformat()
    date_to = now.isoformat()
    
    response = await client.get(
        f"/api/v1/admin/audit-log?date_from={date_from}&date_to={date_to}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should include recent_operation but not old_operation
    operations = [item["operation"] for item in data["items"]]
    assert "recent_operation" in operations
    assert "old_operation" not in operations


@pytest.mark.asyncio
async def test_audit_log_multiple_filters(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    test_enumerator: User,
    admin_token: str,
):
    """Test combining multiple filters."""
    # Create various audit logs
    audit1 = AuditLog(
        user_id=admin_user.id,
        operation="create_user",
        entity_type="user",
        entity_id="1",
    )
    async_db_session.add(audit1)
    
    audit2 = AuditLog(
        user_id=test_enumerator.id,
        operation="create_user",
        entity_type="user",
        entity_id="2",
    )
    async_db_session.add(audit2)
    
    audit3 = AuditLog(
        user_id=admin_user.id,
        operation="update_dropdown",
        entity_type="dropdown_config",
        entity_id="3",
    )
    async_db_session.add(audit3)
    await async_db_session.commit()
    
    # Query with multiple filters
    response = await client.get(
        f"/api/v1/admin/audit-log?user_id={admin_user.id}&operation=create_user&entity_type=user",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only return audit1
    matching_items = [
        item for item in data["items"]
        if item["operation"] == "create_user" and item["entity_type"] == "user"
    ]
    
    for item in matching_items:
        assert item["user"]["id"] == str(admin_user.id)
        assert item["operation"] == "create_user"
        assert item["entity_type"] == "user"


@pytest.mark.asyncio
async def test_audit_log_includes_user_info(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test that audit log entries include user information."""
    # Create an audit log entry
    audit = AuditLog(
        user_id=admin_user.id,
        operation="test_operation",
        entity_type="test",
        entity_id="1",
        detail={"key": "value"},
    )
    async_db_session.add(audit)
    await async_db_session.commit()
    
    # Query audit logs
    response = await client.get(
        "/api/v1/admin/audit-log",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Find our test entry
    test_items = [
        item for item in data["items"]
        if item["operation"] == "test_operation"
    ]
    
    assert len(test_items) > 0
    item = test_items[0]
    
    # Verify structure
    assert "id" in item
    assert "timestamp" in item
    assert "user" in item
    assert "operation" in item
    assert "entity_type" in item
    assert "entity_id" in item
    assert "detail" in item
    
    # Verify user info
    assert item["user"] is not None
    assert item["user"]["id"] == str(admin_user.id)
    assert item["user"]["username"] == admin_user.username
    assert item["user"]["email"] == admin_user.email
    
    # Verify other fields
    assert item["operation"] == "test_operation"
    assert item["entity_type"] == "test"
    assert item["detail"] == {"key": "value"}


@pytest.mark.asyncio
async def test_audit_log_invalid_user_id_format(
    client: AsyncClient,
    admin_token: str,
):
    """Test that invalid user_id format returns 400."""
    response = await client.get(
        "/api/v1/admin/audit-log?user_id=invalid-uuid",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 400
    assert "Invalid user_id format" in response.json()["details"]


@pytest.mark.asyncio
async def test_audit_log_invalid_date_format(
    client: AsyncClient,
    admin_token: str,
):
    """Test that invalid date format returns 400."""
    response = await client.get(
        "/api/v1/admin/audit-log?date_from=invalid-date",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 400
    assert "Invalid date_from format" in response.json()["details"]
    
    response = await client.get(
        "/api/v1/admin/audit-log?date_to=invalid-date",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 400
    assert "Invalid date_to format" in response.json()["details"]


@pytest.mark.asyncio
async def test_audit_log_handles_null_user_id(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_token: str,
):
    """Test that audit logs with null user_id are handled correctly."""
    # Create an audit log entry with null user_id (system operation)
    audit = AuditLog(
        user_id=None,
        operation="system_operation",
        entity_type="system",
        entity_id="1",
    )
    async_db_session.add(audit)
    await async_db_session.commit()
    
    # Query audit logs
    response = await client.get(
        "/api/v1/admin/audit-log",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Find our system operation
    system_items = [
        item for item in data["items"]
        if item["operation"] == "system_operation"
    ]
    
    if len(system_items) > 0:
        item = system_items[0]
        assert item["user"] is None

