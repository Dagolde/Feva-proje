"""Admin dashboard HTML routes.

Requirements: 1.1, 1.3
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.deps import require_role
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(require_role("admin")),
):
    """Render the admin dashboard home page.
    
    Displays system overview with:
    - System health metrics (database status, disk space, uptime)
    - Record statistics (pending, approved, rejected counts)
    - Quick action buttons for common admin tasks
    - Recent activity summary from audit log
    
    Requirements: 1.1, 1.3
    """
    return templates.TemplateResponse(
        "admin/index.html",
        {"request": request, "user": current_user}
    )


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    current_user: User = Depends(require_role("admin")),
):
    """Render the user management page.
    
    Displays user list table with:
    - Search and filter controls
    - User statistics (total, active, locked)
    - Create user modal
    - Edit user modal (role and LGA assignment)
    - Reset password functionality
    - Deactivate user functionality
    
    All operations use the existing API endpoints at /api/v1/admin/users.
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
    """
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "user": current_user}
    )


@router.get("/admin/roles", response_class=HTMLResponse)
async def admin_roles(
    request: Request,
    current_user: User = Depends(require_role("admin")),
):
    """Render the role management page.
    
    Displays role definitions with:
    - Role list with permissions
    - User count per role
    - Role descriptions and capabilities
    
    This is a read-only view. Role assignment happens via the user management page.
    Role definitions are system-managed and cannot be modified through the interface.
    
    Requirements: 5.1, 5.2, 5.3
    """
    return templates.TemplateResponse(
        "admin/roles.html",
        {"request": request, "user": current_user}
    )


@router.get("/admin/config", response_class=HTMLResponse)
async def admin_config(
    request: Request,
    current_user: User = Depends(require_role("admin")),
):
    """Render the system configuration page.
    
    Displays two main sections:
    1. Dropdown Configuration Editor:
       - View all dropdown options with category filter
       - Create new dropdown options for building types, street types, etc.
       - Edit existing dropdown labels and sort order
       - Delete dropdown options
    
    2. LGA Assignment Interface:
       - View LGA assignments for enumerators and supervisors
       - Edit LGA assignments for field staff
       - Filter by role and search by username
    
    All operations use the existing API endpoints:
    - /api/v1/admin/dropdown-config for dropdown CRUD
    - /api/v1/admin/users for LGA assignment updates
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    return templates.TemplateResponse(
        "admin/config.html",
        {"request": request, "user": current_user}
    )


@router.get("/admin/shapefiles", response_class=HTMLResponse)
async def admin_shapefiles(
    request: Request,
    current_user: User = Depends(require_role("admin")),
):
    """Render the shapefile management page.
    
    Displays shapefile upload interface and version history:
    1. Upload Interface:
       - Layer name input (e.g., lga, ward, nipost)
       - Version tag input (e.g., 2025-Q1)
       - File upload with validation (ZIP format, max 50MB)
       - Upload progress indicator
    
    2. Version History Table:
       - List all uploaded shapefile versions
       - Display layer name, version tag, upload timestamp, uploader
       - Show active/inactive status
       - Display SHA-256 checksum (truncated, click to copy full)
       - Activation controls to mark a version as active
    
    All operations use the existing API endpoints:
    - POST /api/v1/admin/shapefiles for upload
    - GET /api/v1/admin/shapefiles for listing versions
    - PATCH /api/v1/admin/shapefiles/{id}/activate for activation
    
    Requirements: 7.1, 7.4, 7.5
    """
    return templates.TemplateResponse(
        "admin/shapefiles.html",
        {"request": request, "user": current_user}
    )


@router.get("/admin/export", response_class=HTMLResponse)
async def admin_export(
    request: Request,
    current_user: User = Depends(require_role("admin")),
):
    """Render the data export page.
    
    Displays export interface with:
    1. Export Configuration:
       - Export type selection (building, street, audit_log)
       - Format selection (CSV, GeoJSON)
       - Filter options (LGA, ward, status, date range)
       - Create export button
    
    2. Export Tasks List:
       - List all export tasks with status
       - Display task details (type, format, filters, created/completed time)
       - Download links for completed exports
       - Auto-refresh every 10 seconds for status updates
    
    All operations use the existing API endpoints:
    - POST /api/v1/admin/export for creating export tasks
    - GET /api/v1/admin/export/{task_id} for checking status
    - GET /api/v1/admin/export/download/{task_id} for downloading files
    - POST /api/v1/admin/export/audit-log for audit log exports
    
    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
    """
    return templates.TemplateResponse(
        "admin/export.html",
        {"request": request, "user": current_user}
    )


@router.get("/admin/monitoring", response_class=HTMLResponse)
async def admin_monitoring(
    request: Request,
    current_user: User = Depends(require_role("admin")),
):
    """Render the system monitoring page.
    
    Displays real-time monitoring dashboard with:
    1. System Health Dashboard:
       - Database connection status
       - Available disk space
       - System uptime
       - Last health check timestamp
    
    2. Record Statistics:
       - Counts by status (pending, approved, rejected, flagged)
       - Visual indicators for each status
    
    3. User Statistics:
       - Active user counts by role (admin, qa_officer, supervisor, enumerator)
    
    4. Sync Session Logs:
       - Recent sync sessions with device ID, user, status, timestamps
       - Pagination support (20 sessions per page)
       - Status filter (all, completed, failed, in_progress)
       - View detailed logs for failed sessions
    
    Auto-refresh every 30 seconds for real-time monitoring.
    Manual refresh button available for immediate updates.
    
    All data fetched from existing API endpoints:
    - GET /api/v1/admin/monitoring/health for system health metrics
    - GET /api/v1/admin/monitoring/statistics for record and user counts
    - GET /api/v1/admin/monitoring/sync-sessions for sync session logs
    
    Requirements: 9.1, 9.2, 9.3, 9.4, 9.6
    """
    return templates.TemplateResponse(
        "admin/monitoring.html",
        {"request": request, "user": current_user}
    )


@router.get("/admin/audit", response_class=HTMLResponse)
async def admin_audit(
    request: Request,
    current_user: User = Depends(require_role("admin")),
):
    """Render the audit log viewer page.
    
    Displays paginated audit log with comprehensive filtering:
    1. Filter Controls:
       - User dropdown (filter by user who performed action)
       - Operation dropdown (filter by operation type)
       - Entity type dropdown (filter by entity type)
       - Date range filters (from/to dates)
       - Clear filters button
    
    2. Audit Log Table:
       - Timestamp (when action occurred)
       - User (who performed the action)
       - Operation (what action was performed)
       - Entity Type (what type of entity was affected)
       - Entity ID (specific entity identifier)
       - Details (JSON details, click to view full)
    
    3. Pagination Controls:
       - Page size selection (10, 25, 50, 100 entries per page)
       - Previous/Next page navigation
       - Entry count display
    
    4. Detail Modal:
       - Click any entry to view full details
       - Shows complete JSON detail in formatted view
       - Displays all metadata including user email
    
    All data fetched from existing API endpoint:
    - GET /api/v1/admin/audit-log with pagination and filters
    
    Supports filters for user_id, operation, entity_type, and date range.
    Returns audit entries ordered by timestamp descending (newest first).
    
    Requirements: Task 16.8
    """
    return templates.TemplateResponse(
        "admin/audit.html",
        {"request": request, "user": current_user}
    )
