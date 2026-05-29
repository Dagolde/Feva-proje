"""Tests for admin export API endpoints.

Requirements: 8.4, 18.5, 18.7
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.building import Building
from app.models.export_task import ExportTask
from app.models.role import Role
from app.models.street import Street
from app.models.user import User


@pytest.mark.asyncio
async def test_create_export_task_csv_building(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test creating a CSV export task for buildings."""
    response = await client.post(
        "/api/v1/admin/export",
        json={
            "format": "csv",
            "entity_type": "building",
            "filters": {"lga": "Lagos", "status": "approved"},
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    
    # Verify task was created in database
    task_id = uuid.UUID(data["task_id"])
    result = await async_db_session.execute(select(ExportTask).where(ExportTask.id == task_id))
    task = result.scalar_one()
    assert task.format == "csv"
    assert task.entity_type == "building"
    assert task.filters == {"lga": "Lagos", "status": "approved"}
    assert task.created_by == admin_user.id


@pytest.mark.asyncio
async def test_create_export_task_geojson_street(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test creating a GeoJSON export task for streets."""
    response = await client.post(
        "/api/v1/admin/export",
        json={
            "format": "geojson",
            "entity_type": "street",
            "filters": {"ward": "Ward1"},
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_create_export_task_invalid_format(
    client: AsyncClient,
    admin_token: str,
):
    """Test creating export task with invalid format."""
    response = await client.post(
        "/api/v1/admin/export",
        json={
            "format": "xml",  # Invalid format
            "entity_type": "building",
            "filters": {},
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 400
    assert "Format must be" in response.json()["details"]


@pytest.mark.asyncio
async def test_create_export_task_invalid_entity_type(
    client: AsyncClient,
    admin_token: str,
):
    """Test creating export task with invalid entity type."""
    response = await client.post(
        "/api/v1/admin/export",
        json={
            "format": "csv",
            "entity_type": "user",  # Invalid entity type
            "filters": {},
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 400
    assert "Entity type must be" in response.json()["details"]


@pytest.mark.asyncio
async def test_get_export_status_pending(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test getting status of a pending export task."""
    # Create a pending export task
    task = ExportTask(
        created_by=admin_user.id,
        format="csv",
        entity_type="building",
        filters={},
        status="pending",
    )
    async_db_session.add(task)
    await async_db_session.flush()
    await async_db_session.commit()
    
    response = await client.get(
        f"/api/v1/admin/export/{task.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert "download_url" not in data


@pytest.mark.asyncio
async def test_get_export_status_completed(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test getting status of a completed export task."""
    # Create a completed export task
    task = ExportTask(
        created_by=admin_user.id,
        format="csv",
        entity_type="building",
        filters={},
        status="completed",
        file_path="exports/test.csv",
    )
    async_db_session.add(task)
    await async_db_session.flush()
    await async_db_session.commit()
    
    response = await client.get(
        f"/api/v1/admin/export/{task.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "download_url" in data
    assert f"/api/v1/admin/export/download/{task.id}" in data["download_url"]


@pytest.mark.asyncio
async def test_get_export_status_failed(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test getting status of a failed export task."""
    # Create a failed export task
    task = ExportTask(
        created_by=admin_user.id,
        format="csv",
        entity_type="building",
        filters={},
        status="failed",
        error_message="Database connection error",
    )
    async_db_session.add(task)
    await async_db_session.flush()
    await async_db_session.commit()
    
    response = await client.get(
        f"/api/v1/admin/export/{task.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error"] == "Database connection error"


@pytest.mark.asyncio
async def test_get_export_status_not_found(
    client: AsyncClient,
    admin_token: str,
):
    """Test getting status of non-existent export task."""
    fake_task_id = uuid.uuid4()
    response = await client.get(
        f"/api/v1/admin/export/{fake_task_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_export_file(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
    tmp_path: Path,
):
    """Test downloading a completed export file."""
    # Create a test export file
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    test_file = export_dir / "test_export.csv"
    test_file.write_text("id,name\n1,Test\n")
    
    # Create a completed export task
    task = ExportTask(
        created_by=admin_user.id,
        format="csv",
        entity_type="building",
        filters={},
        status="completed",
        file_path=str(test_file),
    )
    async_db_session.add(task)
    await async_db_session.flush()
    await async_db_session.commit()
    
    try:
        response = await client.get(
            f"/api/v1/admin/export/download/{task.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "id,name" in response.text
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


@pytest.mark.asyncio
async def test_download_export_file_not_ready(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test downloading export file when task is not completed."""
    # Create a pending export task
    task = ExportTask(
        created_by=admin_user.id,
        format="csv",
        entity_type="building",
        filters={},
        status="pending",
    )
    async_db_session.add(task)
    await async_db_session.flush()
    await async_db_session.commit()
    
    response = await client.get(
        f"/api/v1/admin/export/download/{task.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 404
    assert "not ready" in response.json()["details"]


@pytest.mark.asyncio
async def test_export_audit_log(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: User,
    admin_token: str,
):
    """Test creating an audit log export task."""
    response = await client.post(
        "/api/v1/admin/export/audit-log",
        json={"user_id": str(admin_user.id)},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    
    # Verify task was created with correct entity_type
    task_id = uuid.UUID(data["task_id"])
    result = await async_db_session.execute(select(ExportTask).where(ExportTask.id == task_id))
    task = result.scalar_one()
    assert task.entity_type == "audit_log"
    assert task.format == "csv"


@pytest.mark.asyncio
async def test_export_endpoints_require_admin_role(
    client: AsyncClient,
    enumerator_token: str,
):
    """Test that export endpoints require admin role."""
    # Test create export
    response = await client.post(
        "/api/v1/admin/export",
        json={
            "format": "csv",
            "entity_type": "building",
            "filters": {},
        },
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    assert response.status_code == 403
    
    # Test get status
    fake_task_id = uuid.uuid4()
    response = await client.get(
        f"/api/v1/admin/export/{fake_task_id}",
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    assert response.status_code == 403
    
    # Test download
    response = await client.get(
        f"/api/v1/admin/export/download/{fake_task_id}",
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    assert response.status_code == 403
    
    # Test audit log export
    response = await client.post(
        "/api/v1/admin/export/audit-log",
        json={},
        headers={"Authorization": f"Bearer {enumerator_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_export_endpoints_require_authentication(
    client: AsyncClient,
):
    """Test that export endpoints require authentication."""
    # Test create export
    response = await client.post(
        "/api/v1/admin/export",
        json={
            "format": "csv",
            "entity_type": "building",
            "filters": {},
        },
    )
    assert response.status_code == 401
    
    # Test get status
    fake_task_id = uuid.uuid4()
    response = await client.get(f"/api/v1/admin/export/{fake_task_id}")
    assert response.status_code == 401
    
    # Test download
    response = await client.get(f"/api/v1/admin/export/download/{fake_task_id}")
    assert response.status_code == 401
    
    # Test audit log export
    response = await client.post("/api/v1/admin/export/audit-log", json={})
    assert response.status_code == 401

