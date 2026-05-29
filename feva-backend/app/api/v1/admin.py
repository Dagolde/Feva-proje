"""Admin API endpoints.

POST /api/v1/admin/shapefiles — ingest a shapefile ZIP (Admin only)
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import User
from app.services.shapefile_service import ShapefileIngestionError, ingest_shapefile

router = APIRouter()


@router.post(
    "/shapefiles",
    summary="Ingest a boundary shapefile ZIP package",
    status_code=status.HTTP_201_CREATED,
)
async def upload_shapefile(
    layer_name: Annotated[str, Form(description="Layer identifier, e.g. 'lga', 'ward', 'nipost'")],
    version_tag: Annotated[str, Form(description="Human-readable version tag, e.g. '2025-Q1'")],
    file: Annotated[UploadFile, File(description="ZIP archive containing .shp or .geojson")],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Accept a ZIP upload, validate, reproject, write to PostGIS, and package for devices.

    - Validates file type, size, and MIME type for security
    - Validates geometry type (Polygon/MultiPolygon) and CRS via Fiona/GDAL.
    - Reprojects to EPSG:4326 via GeoPandas if needed.
    - Repairs invalid geometries with `buffer(0)`; skips unfixable features.
    - Writes to `boundary_zones` PostGIS table via GeoAlchemy2.
    - Computes SHA-256 checksum of the raw ZIP.
    - Packages simplified GeoJSON for device distribution.
    - Deactivates previous `shapefile_versions` rows for the layer.

    Requirements: 8.1, 8.5, 20.7, 20.8
    """
    from app.core.sanitization import validate_file_upload
    
    # Validate filename is provided
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Filename is required",
        )
    
    # Read file content
    zip_bytes = await file.read()
    
    # Validate file upload (extension, size, MIME type)
    is_valid, error_message = validate_file_upload(file.filename, zip_bytes)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_message,
        )

    try:
        result = await ingest_shapefile(
            db=db,
            current_user=current_user,
            layer_name=layer_name,
            version_tag=version_tag,
            zip_bytes=zip_bytes,
        )
    except ShapefileIngestionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # Don't return the raw GeoJSON bytes in the response body.
    return {
        "layer": result["layer"],
        "version": result["version"],
        "checksum_sha256": result["checksum_sha256"],
        "geojson_checksum_sha256": result["geojson_checksum_sha256"],
        "features_written": result["features_written"],
        "features_skipped": result["features_skipped"],
    }


@router.get("/shapefiles", summary="List all shapefile versions (Admin only)")
async def list_shapefiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List all shapefile versions with metadata.
    
    Returns version number, upload timestamp, active status, layer name,
    and uploader information for all shapefile versions in the system.
    
    Requirements: 7.4, 18.4, 18.7
    """
    from app.models.shapefile_version import ShapefileVersion
    
    result = await db.execute(
        _select(ShapefileVersion).order_by(ShapefileVersion.uploaded_at.desc())
    )
    versions = result.scalars().all()
    
    return [
        {
            "id": v.id,
            "layer_name": v.layer_name,
            "version_tag": v.version_tag,
            "checksum_sha256": v.checksum_sha256,
            "uploaded_by": str(v.uploaded_by) if v.uploaded_by else None,
            "uploaded_at": str(v.uploaded_at),
            "is_active": v.is_active,
        }
        for v in versions
    ]


@router.patch("/shapefiles/{id}/activate", summary="Activate shapefile version (Admin only)")
async def activate_shapefile(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Mark a specific shapefile version as active.
    
    Deactivates all other versions for the same layer and activates the
    specified version. Returns 404 if the shapefile ID is not found.
    
    Requirements: 7.5, 18.4, 18.7
    """
    from app.models.shapefile_version import ShapefileVersion
    
    # Fetch the target shapefile version
    result = await db.execute(
        _select(ShapefileVersion).where(ShapefileVersion.id == id)
    )
    target_version = result.scalar_one_or_none()
    
    if not target_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shapefile version with id {id} not found",
        )
    
    # Deactivate all other versions for the same layer
    result = await db.execute(
        _select(ShapefileVersion).where(
            ShapefileVersion.layer_name == target_version.layer_name
        )
    )
    all_versions = result.scalars().all()
    
    for version in all_versions:
        if version.id == id:
            version.is_active = True
        else:
            version.is_active = False
        db.add(version)
    
    await db.flush()
    
    # Log the activation in audit log
    audit = _AuditLog(
        user_id=current_user.id,
        operation="activate_shapefile",
        entity_type="shapefile_version",
        entity_id=str(id),
        detail={
            "layer_name": target_version.layer_name,
            "version_tag": target_version.version_tag,
        },
    )
    db.add(audit)
    await db.commit()
    
    return {"status": "activated"}


# ── User management ───────────────────────────────────────────────────────────

import uuid as _uuid
from pydantic import BaseModel as _BaseModel, EmailStr as _EmailStr

from app.models.audit_log import AuditLog as _AuditLog
from app.models.dropdown_config import DropdownConfig as _DropdownConfig
from app.models.role import Role as _Role
from app.models.user import User as _User
from sqlalchemy import select as _select
from app.services import user_service


class UserCreate(_BaseModel):
    username: str
    email: _EmailStr
    password: str
    role_id: int
    lga_assignment: list[str] | None = None
    ward_assignment: str | None = None


class UserPatch(_BaseModel):
    role_id: int | None = None
    lga_assignment: list[str] | None = None
    ward_assignment: str | None = None
    locked: bool | None = None


class PasswordReset(_BaseModel):
    new_password: str


@router.get("/users", summary="List all users with pagination (Admin only)")
async def list_users(
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List all users with pagination.
    
    Requirements: 18.1, 18.7
    """
    total, users = await user_service.list_users(db, page, page_size)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": str(u.id),
                "username": u.username,
                "email": u.email,
                "role_id": u.role_id,
                "lga_assignment": u.lga_assignment,
                "ward_assignment": u.ward_assignment,
                "totp_enabled": u.totp_enabled,
                "locked_at": u.locked_at,
                "created_at": u.created_at,
            }
            for u in users
        ],
    }


@router.post("/users", status_code=status.HTTP_201_CREATED, summary="Create new user (Admin only)")
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Create a new user account.
    
    Requirements: 18.1, 18.7, 20.2, 20.3
    """
    from app.core.sanitization import sanitize_sql_input
    from app.core.security import validate_password_complexity
    
    # Sanitize text inputs
    try:
        username = sanitize_sql_input(body.username)
        email = sanitize_sql_input(body.email)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    # Validate password complexity
    is_valid, error_message = validate_password_complexity(body.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )
    
    try:
        user = await user_service.create_user(
            db=db,
            username=username,
            email=email,
            password=body.password,
            role_id=body.role_id,
            lga_assignment=body.lga_assignment,
            ward_assignment=body.ward_assignment,
            created_by=current_user.id,
        )
        return {"id": str(user.id), "username": user.username}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/users/{user_id}", summary="Update user role/assignment/lock (Admin only)")
async def patch_user(
    user_id: str,
    body: UserPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Update user account details.
    
    Requirements: 18.1, 18.7
    """
    try:
        user = await user_service.update_user(
            db=db,
            user_id=_uuid.UUID(user_id),
            role_id=body.role_id,
            lga_assignment=body.lga_assignment,
            ward_assignment=body.ward_assignment,
            locked=body.locked,
            updated_by=current_user.id,
        )
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/users/{user_id}", summary="Deactivate user (Admin only)")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Deactivate a user account (soft delete).
    
    Requirements: 18.1, 18.7
    """
    try:
        await user_service.deactivate_user(
            db=db,
            user_id=_uuid.UUID(user_id),
            deactivated_by=current_user.id,
        )
        return {"status": "deactivated"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/users/{user_id}/reset-password", summary="Reset user password (Admin only)")
async def reset_user_password(
    user_id: str,
    body: PasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Reset a user's password.
    
    Requirements: 18.1, 18.7
    """
    from app.core.security import validate_password_complexity
    
    # Validate password complexity
    is_valid, error_message = validate_password_complexity(body.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )
    
    try:
        await user_service.reset_password(
            db=db,
            user_id=_uuid.UUID(user_id),
            new_password=body.new_password,
            reset_by=current_user.id,
        )
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ── Role management ───────────────────────────────────────────────────────────

@router.get("/roles", summary="List all roles with permissions (Admin only)")
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List all roles with their associated permissions.
    
    Returns role definitions for admin, enumerator, supervisor, and qa_officer
    with their respective permission sets.
    
    Requirements: 5.1, 5.2, 5.3, 18.2, 18.7
    """
    result = await db.execute(_select(_Role).order_by(_Role.id))
    roles = result.scalars().all()
    
    # Define permissions for each role
    # These permissions map to the capabilities each role has in the system
    role_permissions = {
        "admin": [
            "manage_users",
            "manage_roles",
            "manage_system_config",
            "manage_shapefiles",
            "export_data",
            "view_audit_logs",
            "view_monitoring",
            "review_records",
            "manage_dropdown_config",
        ],
        "enumerator": [
            "create_records",
            "edit_own_records",
            "upload_photos",
            "sync_data",
        ],
        "supervisor": [
            "create_records",
            "edit_own_records",
            "upload_photos",
            "sync_data",
            "view_team_records",
            "submit_feedback",
        ],
        "qa_officer": [
            "review_records",
            "approve_records",
            "reject_records",
            "view_qa_statistics",
            "view_audit_trail",
        ],
    }
    
    return [
        {
            "id": role.id,
            "name": role.name,
            "permissions": role_permissions.get(role.name, []),
        }
        for role in roles
    ]


# ── Dropdown config ───────────────────────────────────────────────────────────

class DropdownCreate(_BaseModel):
    category: str
    value: str
    label: str
    sort_order: int = 0


@router.get("/dropdown-config", summary="List dropdown config (Admin only)")
async def list_dropdown_config(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List dropdown configuration options with optional category filter.
    
    Requirements: 6.1, 18.3, 18.7
    """
    query = _select(_DropdownConfig).order_by(_DropdownConfig.category, _DropdownConfig.sort_order)
    
    # Apply category filter if provided
    if category:
        query = query.where(_DropdownConfig.category == category)
    
    result = await db.execute(query)
    rows = result.scalars().all()
    return [
        {"id": r.id, "category": r.category, "value": r.value, "label": r.label,
         "sort_order": r.sort_order, "version": r.version}
        for r in rows
    ]


@router.post("/dropdown-config", status_code=status.HTTP_201_CREATED, summary="Add dropdown value (Admin only)")
async def create_dropdown_config(
    body: DropdownCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Create a new dropdown configuration option.
    
    Validates that value and label are not empty or whitespace-only.
    Sanitizes inputs to prevent XSS and SQL injection.
    
    Requirements: 6.2, 6.6, 18.3, 18.7, 20.2, 20.3
    """
    from app.core.sanitization import sanitize_html_input, sanitize_sql_input
    
    # Sanitize inputs
    try:
        category = sanitize_sql_input(body.category)
        value = sanitize_sql_input(body.value)
        label = sanitize_html_input(body.label)  # Label may be displayed in UI
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    # Validate that value and label are not empty or whitespace-only
    if not value or not value.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dropdown value cannot be empty or whitespace-only",
        )
    
    if not label or not label.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dropdown label cannot be empty or whitespace-only",
        )
    
    if not category or not category.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dropdown category cannot be empty or whitespace-only",
        )
    
    # Increment version for this category
    result = await db.execute(
        _select(_DropdownConfig.version)
        .where(_DropdownConfig.category == category)
        .order_by(_DropdownConfig.version.desc())
        .limit(1)
    )
    latest_version = result.scalar() or 0

    row = _DropdownConfig(
        category=category,
        value=value,
        label=label,
        sort_order=body.sort_order,
        version=latest_version + 1,
        created_by=current_user.id,
    )
    db.add(row)
    await db.flush()
    await _write_admin_audit(db, current_user.id, "create_dropdown", str(row.id))
    await db.commit()
    return {"id": row.id, "version": row.version}


class DropdownPatch(_BaseModel):
    label: str | None = None
    sort_order: int | None = None


@router.patch("/dropdown-config/{id}", summary="Update dropdown option (Admin only)")
async def update_dropdown_config(
    id: int,
    body: DropdownPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Update an existing dropdown configuration option.
    
    Only label and sort_order can be updated. Category and value are immutable.
    Sanitizes label input to prevent XSS attacks.
    
    Requirements: 6.3, 6.6, 18.3, 18.7, 20.3
    """
    from app.core.sanitization import sanitize_html_input
    
    # Fetch the existing dropdown config
    result = await db.execute(_select(_DropdownConfig).where(_DropdownConfig.id == id))
    dropdown = result.scalar_one_or_none()
    
    if not dropdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dropdown config with id {id} not found",
        )
    
    # Track changes for audit log
    changes = {}
    
    # Update label if provided
    if body.label is not None:
        # Sanitize label
        sanitized_label = sanitize_html_input(body.label)
        
        # Validate label is not empty or whitespace-only
        if not sanitized_label or not sanitized_label.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dropdown label cannot be empty or whitespace-only",
            )
        if dropdown.label != sanitized_label:
            changes["label"] = {"old": dropdown.label, "new": sanitized_label}
            dropdown.label = sanitized_label
    
    # Update sort_order if provided
    if body.sort_order is not None:
        if dropdown.sort_order != body.sort_order:
            changes["sort_order"] = {"old": dropdown.sort_order, "new": body.sort_order}
            dropdown.sort_order = body.sort_order
    
    # Only commit if there are changes
    if changes:
        db.add(dropdown)
        await db.flush()
        
        # Log the update in audit log
        audit = _AuditLog(
            user_id=current_user.id,
            operation="update_dropdown",
            entity_type="dropdown_config",
            entity_id=str(id),
            detail=changes,
        )
        db.add(audit)
        await db.commit()
    
    return {"status": "ok"}


@router.delete("/dropdown-config/{id}", summary="Delete dropdown option (Admin only)")
async def delete_dropdown_config(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Delete a dropdown configuration option.
    
    Requirements: 6.3, 18.3, 18.7
    """
    # Fetch the existing dropdown config
    result = await db.execute(_select(_DropdownConfig).where(_DropdownConfig.id == id))
    dropdown = result.scalar_one_or_none()
    
    if not dropdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dropdown config with id {id} not found",
        )
    
    # Store details for audit log before deletion
    dropdown_details = {
        "category": dropdown.category,
        "value": dropdown.value,
        "label": dropdown.label,
    }
    
    # Delete the dropdown config
    await db.delete(dropdown)
    await db.flush()
    
    # Log the deletion in audit log
    audit = _AuditLog(
        user_id=current_user.id,
        operation="delete_dropdown",
        entity_type="dropdown_config",
        entity_id=str(id),
        detail=dropdown_details,
    )
    db.add(audit)
    await db.commit()
    
    return {"status": "deleted"}


# ── Audit log ─────────────────────────────────────────────────────────────────

@router.get("/audit-log", summary="Query audit logs with filters (Admin only)")
async def get_audit_log(
    page: int = 1,
    page_size: int = 50,
    user_id: str | None = None,
    operation: str | None = None,
    entity_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Query audit logs with pagination and filtering.
    
    Supports filters for:
    - user_id: Filter by user UUID
    - operation: Filter by operation type (e.g., create_user, update_dropdown)
    - entity_type: Filter by entity type (e.g., user, dropdown_config)
    - date_from: Filter by start date (ISO format)
    - date_to: Filter by end date (ISO format)
    
    Returns audit entries with timestamp (occurred_at), user info, operation,
    entity details, ordered by occurred_at descending (newest first).
    
    Requirements: 18.7
    """
    from sqlalchemy import and_, func
    from datetime import datetime
    
    # Build base query
    q = _select(_AuditLog)
    conditions = []
    
    # Apply user_id filter
    if user_id:
        try:
            user_uuid = _uuid.UUID(user_id)
            conditions.append(_AuditLog.user_id == user_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format. Must be a valid UUID.",
            )
    
    # Apply operation filter
    if operation:
        conditions.append(_AuditLog.operation == operation)
    
    # Apply entity_type filter
    if entity_type:
        conditions.append(_AuditLog.entity_type == entity_type)
    
    # Apply date_from filter
    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            conditions.append(_AuditLog.occurred_at >= date_from_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use ISO 8601 format (e.g., 2024-01-01T00:00:00Z).",
            )
    
    # Apply date_to filter
    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            conditions.append(_AuditLog.occurred_at <= date_to_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use ISO 8601 format (e.g., 2024-01-01T23:59:59Z).",
            )
    
    # Apply all conditions
    if conditions:
        q = q.where(and_(*conditions))
    
    # Get total count
    count_query = _select(func.count()).select_from(_AuditLog)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Order by occurred_at descending (newest first)
    q = q.order_by(_AuditLog.occurred_at.desc())
    
    # Apply pagination
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    logs = result.scalars().all()
    
    # Fetch user information for each log entry
    items = []
    for log in logs:
        user_info = None
        if log.user_id:
            user_result = await db.execute(
                _select(_User).where(_User.id == log.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                user_info = {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                }
        
        items.append({
            "id": log.id,
            "timestamp": str(log.occurred_at),
            "user": user_info,
            "operation": log.operation,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "detail": log.detail,
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


# ── Shared helper ─────────────────────────────────────────────────────────────

async def _write_admin_audit(
    db: AsyncSession,
    user_id: _uuid.UUID,
    operation: str,
    entity_id: str,
) -> None:
    log = _AuditLog(
        user_id=user_id,
        operation=operation,
        entity_type="admin",
        entity_id=entity_id,
    )
    db.add(log)
    await db.flush()


# ── Export endpoints ──────────────────────────────────────────────────────────

from fastapi import BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path as _Path


class ExportCreate(_BaseModel):
    format: str  # csv, geojson
    entity_type: str  # building, street, audit_log
    filters: dict = {}


@router.post("/export", status_code=status.HTTP_201_CREATED, summary="Create export task (Admin only)")
async def create_export(
    body: ExportCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Create a new export task for buildings, streets, or audit log.
    
    Accepts format (csv, geojson), entity_type (building, street, audit_log),
    and optional filters (lga, ward, status, date_from, date_to).
    
    Returns task_id for polling export status.
    
    Requirements: 8.4, 18.5, 18.7
    """
    from app.services import export_service
    
    # Validate format
    if body.format not in ("csv", "geojson"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'csv' or 'geojson'",
        )
    
    # Validate entity_type
    if body.entity_type not in ("building", "street", "audit_log"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entity type must be 'building', 'street', or 'audit_log'",
        )
    
    # Create export task
    task_id = await export_service.create_export_task(
        db=db,
        format=body.format,
        entity_type=body.entity_type,
        filters=body.filters,
        created_by=current_user.id,
    )
    
    # Start background processing
    if body.format == "csv":
        background_tasks.add_task(
            export_service.generate_csv_export,
            db,
            task_id,
            body.entity_type,
            body.filters,
        )
    elif body.format == "geojson":
        background_tasks.add_task(
            export_service.generate_geojson_export,
            db,
            task_id,
            body.entity_type,
            body.filters,
        )
    
    return {"task_id": str(task_id), "status": "pending"}


@router.get("/export/tasks", summary="List all export tasks (Admin only)")
async def list_export_tasks(
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List all export tasks with pagination.
    
    Returns a paginated list of export tasks ordered by creation date (newest first).
    Includes task details: id, entity_type, format, filters, status, created_at, completed_at.
    
    Requirements: 8.4, 18.5, 18.7
    """
    from app.models.export_task import ExportTask
    from sqlalchemy import func as _func
    
    # Get total count
    count_result = await db.execute(
        _select(_func.count()).select_from(ExportTask)
    )
    total = count_result.scalar() or 0
    
    # Get paginated results
    result = await db.execute(
        _select(ExportTask)
        .order_by(ExportTask.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    tasks = result.scalars().all()
    
    # Format response
    items = []
    for task in tasks:
        items.append({
            "id": str(task.id),
            "entity_type": task.entity_type,
            "format": task.format,
            "filters": task.filters or {},
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error_message": task.error_message,
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get("/export/{task_id}", summary="Get export status (Admin only)")
async def get_export_status_endpoint(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Get the status of an export task.
    
    Returns status (pending, processing, completed, failed), download_url if completed,
    and error message if failed.
    
    Requirements: 8.4, 18.5, 18.7
    """
    from app.services import export_service
    
    try:
        status_info = await export_service.get_export_status(
            db=db,
            task_id=_uuid.UUID(task_id),
        )
        return status_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/export/download/{task_id}", summary="Download export file (Admin only)")
async def download_export_file(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Download the completed export file.
    
    Returns the file as a downloadable attachment. Returns 404 if task not found
    or file not ready.
    
    Requirements: 8.4, 18.5, 18.7
    """
    from app.models.export_task import ExportTask
    
    # Fetch the export task
    result = await db.execute(
        _select(ExportTask).where(ExportTask.id == _uuid.UUID(task_id))
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Export task {task_id} not found",
        )
    
    if task.status != "completed" or not task.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not ready or task not completed",
        )
    
    # Check if file exists
    file_path = _Path(task.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not found on disk",
        )
    
    # Determine media type based on format
    media_type = "text/csv" if task.format == "csv" else "application/geo+json"
    
    # Return file as download
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=f"{task.entity_type}_export_{task_id}.{task.format}",
    )


@router.post("/export/audit-log", status_code=status.HTTP_201_CREATED, summary="Export audit log to CSV (Admin only)")
async def export_audit_log(
    background_tasks: BackgroundTasks,
    filters: dict = {},
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Export audit log to CSV format.
    
    This is a convenience endpoint that creates an export task for audit_log entity type.
    Returns task_id for polling export status.
    
    Requirements: 8.4, 18.5, 18.7
    """
    from app.services import export_service
    
    # Create export task for audit log
    task_id = await export_service.create_export_task(
        db=db,
        format="csv",
        entity_type="audit_log",
        filters=filters,
        created_by=current_user.id,
    )
    
    # Start background processing
    background_tasks.add_task(
        export_service.generate_csv_export,
        db,
        task_id,
        "audit_log",
        filters,
    )
    
    return {"task_id": str(task_id), "status": "pending"}


# ── Field pilot feedback ───────────────────────────────────────────────────────

from pydantic import BaseModel as _FeedbackBase


class PilotFeedbackCreate(_FeedbackBase):
    device_id: str
    submitted_by: str
    lga: str | None = None
    category: str | None = None
    message: str
    metadata: dict | None = None


@router.post(
    "/pilot-feedback",
    status_code=status.HTTP_201_CREATED,
    summary="Submit UAT pilot feedback (Supervisor only)",
)
async def submit_pilot_feedback(
    body: PilotFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),
) -> dict:
    """Accept structured feedback from Supervisor devices during UAT.

    Stored in `pilot_feedback` table (not part of certified dataset).
    Admin-readable only via GET /api/v1/admin/pilot-feedback.
    Sanitizes message input to prevent XSS attacks.

    Requirements: 20.2, 20.3
    """
    from app.core.sanitization import sanitize_html_input, sanitize_sql_input
    from app.models.pilot_feedback import PilotFeedback

    # Sanitize text inputs
    try:
        device_id = sanitize_sql_input(body.device_id)
        submitted_by = sanitize_sql_input(body.submitted_by)
        lga = sanitize_sql_input(body.lga) if body.lga else None
        category = sanitize_sql_input(body.category) if body.category else None
        message = sanitize_html_input(body.message)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    row = PilotFeedback(
        device_id=device_id,
        submitted_by=submitted_by,
        lga=lga,
        category=category,
        message=message,
        metadata=body.metadata,
    )
    db.add(row)
    await db.flush()
    await _write_admin_audit(db, current_user.id, "submit_pilot_feedback", str(row.id))
    await db.commit()
    return {"id": str(row.id)}


@router.get(
    "/pilot-feedback",
    summary="List UAT pilot feedback (Admin only)",
)
async def list_pilot_feedback(
    lga: str | None = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    from app.models.pilot_feedback import PilotFeedback

    q = _select(PilotFeedback).order_by(PilotFeedback.created_at.desc())
    if lga:
        q = q.where(PilotFeedback.lga == lga)

    result = await db.execute(q.offset((page - 1) * page_size).limit(page_size))
    rows = result.scalars().all()
    return {
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": str(r.id),
                "device_id": r.device_id,
                "submitted_by": r.submitted_by,
                "lga": r.lga,
                "category": r.category,
                "message": r.message,
                "metadata": r.metadata,
                "created_at": str(r.created_at),
            }
            for r in rows
        ],
    }


# ============================================================================
# Monitoring Endpoints
# ============================================================================

@router.get(
    "/monitoring/health",
    summary="Get system health metrics (Admin only)",
)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Return system health metrics including database connectivity, disk space, and uptime.
    
    Requirements: 9.2, 18.6, 18.7
    """
    import os
    import shutil
    import time
    from datetime import datetime, timezone
    
    # Check database connectivity
    try:
        await db.execute(_select(1))
        database_status = "connected"
    except Exception as e:
        database_status = f"error: {str(e)}"
    
    # Get disk space (for the current working directory)
    try:
        stat = shutil.disk_usage(os.getcwd())
        disk_space_gb = stat.free / (1024 ** 3)  # Convert bytes to GB
    except Exception:
        disk_space_gb = 0.0
    
    # Calculate uptime (using process start time as approximation)
    # In production, this would ideally track application start time
    try:
        import psutil
        process = psutil.Process(os.getpid())
        uptime_seconds = int(time.time() - process.create_time())
    except Exception:
        # Fallback if psutil is not available
        uptime_seconds = 0
    
    return {
        "database": database_status,
        "disk_space_gb": round(disk_space_gb, 2),
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/monitoring/sync-sessions",
    summary="Get recent sync sessions (Admin only)",
)
async def get_sync_sessions(
    page: int = 1,
    page_size: int = 50,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """List recent sync sessions with pagination and optional status filter.
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50)
    - status: Filter by status (optional: in_progress, completed, failed)
    
    Requirements: 9.1, 18.6, 18.7
    """
    from sqlalchemy import func
    from app.models.sync_session import SyncSession
    
    # Build query
    query = _select(SyncSession)
    
    # Apply status filter if provided
    if status:
        query = query.where(SyncSession.status == status)
    
    # Get total count
    count_query = _select(func.count()).select_from(SyncSession)
    if status:
        count_query = count_query.where(SyncSession.status == status)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Get paginated results
    query = query.order_by(SyncSession.started_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    # Get user information for each session
    items = []
    for session in sessions:
        user_result = await db.execute(
            _select(_User).where(_User.id == session.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        items.append({
            "id": str(session.id),
            "user_id": str(session.user_id),
            "username": user.username if user else "unknown",
            "device_id": session.device_id,
            "started_at": str(session.started_at),
            "completed_at": str(session.completed_at) if session.completed_at else None,
            "records_received": session.records_received,
            "records_accepted": session.records_accepted,
            "records_rejected": session.records_rejected,
            "records_synced": session.records_accepted,
            "status": session.status,
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get(
    "/monitoring/sync-sessions/{session_id}",
    summary="Get a single sync session detail (Admin only)",
)
async def get_sync_session_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Return full detail for a single sync session by ID.

    Requirements: 9.1
    """
    import uuid as _uuid
    from app.models.sync_session import SyncSession

    try:
        sid = _uuid.UUID(session_id)
    except ValueError:
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=400, detail="Invalid session ID format")

    result = await db.execute(_select(SyncSession).where(SyncSession.id == sid))
    session = result.scalar_one_or_none()

    if session is None:
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=404, detail="Sync session not found")

    user_result = await db.execute(_select(_User).where(_User.id == session.user_id))
    user = user_result.scalar_one_or_none()

    return {
        "id": str(session.id),
        "user_id": str(session.user_id),
        "username": user.username if user else "unknown",
        "device_id": session.device_id,
        "started_at": str(session.started_at),
        "completed_at": str(session.completed_at) if session.completed_at else None,
        "records_received": session.records_received,
        "records_accepted": session.records_accepted,
        "records_rejected": session.records_rejected,
        "records_synced": session.records_accepted,
        "status": session.status,
        "error_message": getattr(session, "error_message", None),
    }


@router.get(
    "/monitoring/statistics",
    summary="Get system statistics (Admin only)",
)
async def get_system_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Return record counts by status and user counts by role.
    
    Requirements: 9.3, 9.4, 18.6, 18.7
    """
    from sqlalchemy import func
    from app.models.building import Building
    from app.models.street import Street
    
    # Count buildings by verification status
    building_status_query = _select(
        Building.verification_status,
        func.count(Building.id).label("count")
    ).group_by(Building.verification_status)
    
    building_result = await db.execute(building_status_query)
    building_counts = {row[0]: row[1] for row in building_result.all()}
    
    # Count streets by verification status
    street_status_query = _select(
        Street.verification_status,
        func.count(Street.id).label("count")
    ).group_by(Street.verification_status)
    
    street_result = await db.execute(street_status_query)
    street_counts = {row[0]: row[1] for row in street_result.all()}
    
    # Combine building and street counts
    all_statuses = set(building_counts.keys()) | set(street_counts.keys())
    records_by_status = {}
    for status in all_statuses:
        records_by_status[status] = (
            building_counts.get(status, 0) + street_counts.get(status, 0)
        )
    
    # Count users by role
    user_role_query = _select(
        _Role.name,
        func.count(_User.id).label("count")
    ).join(_User, _User.role_id == _Role.id).group_by(_Role.name)
    
    user_result = await db.execute(user_role_query)
    users_by_role = {row[0]: row[1] for row in user_result.all()}
    
    return {
        "records_by_status": records_by_status,
        "users_by_role": users_by_role,
    }
