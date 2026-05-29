# Design Document: Admin and QA Dashboards

## Overview

This design implements two separate role-based web dashboards for the FEVA system: an Admin Dashboard at `/admin/` and a QA Dashboard at `/qa/`. The dashboards provide distinct interfaces tailored to their respective user roles while sharing common authentication and authorization infrastructure.

The Admin Dashboard provides comprehensive system administration capabilities including user management, role assignment, system configuration, shapefile management, data export, and monitoring. The QA Dashboard focuses on record review workflows, enabling QA officers to view, filter, approve, and reject enumeration records with detailed audit trails.

Both dashboards are server-rendered HTML applications using Jinja2 templates with progressive enhancement via vanilla JavaScript. This approach ensures compatibility with the existing FastAPI backend architecture while providing responsive, interactive user experiences.

### Key Design Decisions

1. **Server-Side Rendering**: Use Jinja2 templates for initial page load with AJAX for dynamic updates, avoiding the complexity of a separate frontend framework
2. **Role-Based Access Control**: Leverage existing JWT authentication with role-based middleware to enforce access restrictions
3. **RESTful API Design**: Implement comprehensive REST endpoints that can serve both the web dashboards and potential future API consumers
4. **Progressive Enhancement**: Build functional HTML-first interfaces enhanced with JavaScript for better UX
5. **Shared Components**: Reuse authentication, database models, and service layer logic across both dashboards

## Architecture

### System Context

```
┌─────────────────┐
│  Web Browser    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  ┌───────────────────────────────────┐  │
│  │   Authentication Middleware       │  │
│  │   (JWT Token Validation)          │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────┬───────────────────┐  │
│  │ Admin Routes  │  QA Routes        │  │
│  │ /admin/*      │  /qa/*            │  │
│  └───────┬───────┴────────┬──────────┘  │
│          │                │             │
│  ┌───────▼────────────────▼──────────┐  │
│  │     API Layer (v1)                │  │
│  │  /api/v1/admin/*                  │  │
│  │  /api/v1/qa/*                     │  │
│  └───────┬───────────────────────────┘  │
│          │                              │
│  ┌───────▼───────────────────────────┐  │
│  │     Service Layer                 │  │
│  │  - AuthService                    │  │
│  │  - UserService                    │  │
│  │  - QAService                      │  │
│  │  - ExportService                  │  │
│  │  - ShapefileService               │  │
│  └───────┬───────────────────────────┘  │
│          │                              │
│  ┌───────▼───────────────────────────┐  │
│  │     Data Access Layer             │  │
│  │  SQLAlchemy ORM + PostgreSQL      │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Component Architecture

#### Frontend Layer

The frontend consists of server-rendered HTML templates with JavaScript enhancements:

- **Template Engine**: Jinja2 for server-side rendering
- **CSS Framework**: Minimal custom CSS with responsive grid layout
- **JavaScript**: Vanilla JS for AJAX requests, form handling, and dynamic updates
- **State Management**: Server-side session state via JWT tokens in HTTP-only cookies

#### Backend Layer

The backend extends the existing FastAPI application:

- **Web Routes**: HTML-serving endpoints at `/admin/` and `/qa/`
- **API Routes**: RESTful JSON endpoints at `/api/v1/admin/*` and `/api/v1/qa/*`
- **Middleware**: JWT authentication and role-based authorization
- **Services**: Business logic layer for user management, QA operations, exports, etc.
- **Models**: SQLAlchemy ORM models for database entities

### Authentication Flow

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│  Client  │                │  Server  │                │ Database │
└────┬─────┘                └────┬─────┘                └────┬─────┘
     │                           │                           │
     │ POST /api/v1/auth/login   │                           │
     │ {username, password}      │                           │
     ├──────────────────────────►│                           │
     │                           │ Query user by username    │
     │                           ├──────────────────────────►│
     │                           │                           │
     │                           │◄──────────────────────────┤
     │                           │ User record + role        │
     │                           │                           │
     │                           │ Verify password hash      │
     │                           │ Generate JWT with role    │
     │                           │                           │
     │◄──────────────────────────┤                           │
     │ Set-Cookie: token=JWT     │                           │
     │ {access_token, role}      │                           │
     │                           │                           │
     │ GET /admin/               │                           │
     │ Cookie: token=JWT         │                           │
     ├──────────────────────────►│                           │
     │                           │ Decode JWT                │
     │                           │ Check role == "admin"     │
     │                           │                           │
     │◄──────────────────────────┤                           │
     │ 200 OK (HTML dashboard)   │                           │
     │                           │                           │
```

## Components and Interfaces

### Frontend Components

#### Admin Dashboard Pages

1. **Dashboard Home** (`/admin/`)
   - System health metrics
   - Recent activity summary
   - Quick action buttons

2. **User Management** (`/admin/users`)
   - User list table with search/filter
   - Create user modal
   - Edit user modal
   - Password reset functionality

3. **Role Management** (`/admin/roles`)
   - Role list with permissions display
   - Role assignment interface

4. **System Configuration** (`/admin/config`)
   - Dropdown configuration editor
   - LGA assignment interface

5. **Shapefile Management** (`/admin/shapefiles`)
   - Upload interface
   - Version history table
   - Activation controls

6. **Data Export** (`/admin/export`)
   - Export format selection (CSV, GeoJSON)
   - Filter configuration
   - Download links

7. **Monitoring** (`/admin/monitoring`)
   - Sync session logs
   - System health dashboard
   - Record statistics

8. **Audit Log** (`/admin/audit`)
   - Paginated audit log viewer
   - Filter by user, operation, date

#### QA Dashboard Pages

1. **Dashboard Home** (`/qa/`)
   - QA statistics summary
   - Pending records count
   - Recent activity

2. **Record List** (`/qa/records`)
   - Paginated record table
   - Multi-dimensional filters (status, LGA, ward, enumerator, date)
   - Quick status indicators

3. **Record Detail** (`/qa/records/{id}`)
   - Complete record information
   - Photo gallery
   - Interactive map
   - Approval/rejection controls
   - Audit trail

4. **Reports** (`/qa/reports`)
   - QA statistics by enumerator
   - Approval rate charts
   - Review time metrics

5. **Flagged Records** (`/qa/flagged`)
   - Records with QA flags
   - Bulk review interface

### Backend API Endpoints

#### Authentication Endpoints

```
POST   /api/v1/auth/login
  Request: {username: str, password: str}
  Response: {access_token: str, token_type: str, role: str}
  
POST   /api/v1/auth/logout
  Response: {status: str}
  
GET    /api/v1/auth/me
  Response: {id: uuid, username: str, email: str, role: str}
```

#### Admin API Endpoints

```
# User Management
GET    /api/v1/admin/users
  Query: ?page=1&page_size=50
  Response: {total: int, items: [User]}
  
POST   /api/v1/admin/users
  Request: {username: str, email: str, password: str, role_id: int, lga_assignment: [str]}
  Response: {id: uuid, username: str}
  
PATCH  /api/v1/admin/users/{user_id}
  Request: {role_id?: int, lga_assignment?: [str], locked?: bool}
  Response: {status: str}
  
DELETE /api/v1/admin/users/{user_id}
  Response: {status: str}
  
POST   /api/v1/admin/users/{user_id}/reset-password
  Request: {new_password: str}
  Response: {status: str}

# Role Management
GET    /api/v1/admin/roles
  Response: [{id: int, name: str, permissions: [str]}]

# Dropdown Configuration
GET    /api/v1/admin/dropdown-config
  Query: ?category=building_type
  Response: [{id: int, category: str, value: str, label: str, sort_order: int}]
  
POST   /api/v1/admin/dropdown-config
  Request: {category: str, value: str, label: str, sort_order: int}
  Response: {id: int, version: int}
  
PATCH  /api/v1/admin/dropdown-config/{id}
  Request: {label?: str, sort_order?: int}
  Response: {status: str}
  
DELETE /api/v1/admin/dropdown-config/{id}
  Response: {status: str}

# Shapefile Management
POST   /api/v1/admin/shapefiles
  Request: multipart/form-data {layer_name: str, version_tag: str, file: File}
  Response: {layer: str, version: str, checksum_sha256: str, features_written: int}
  
GET    /api/v1/admin/shapefiles
  Response: [{id: int, layer: str, version: str, active: bool, uploaded_at: str}]
  
PATCH  /api/v1/admin/shapefiles/{id}/activate
  Response: {status: str}

# Data Export
POST   /api/v1/admin/export
  Request: {format: str, entity_type: str, filters: {lga?: str, ward?: str, status?: str, date_from?: str, date_to?: str}}
  Response: {task_id: uuid, status: str}
  
GET    /api/v1/admin/export/{task_id}
  Response: {status: str, download_url?: str, error?: str}

# Monitoring
GET    /api/v1/admin/monitoring/health
  Response: {database: str, disk_space_gb: float, uptime_seconds: int}
  
GET    /api/v1/admin/monitoring/sync-sessions
  Query: ?page=1&page_size=50&status=failed
  Response: {total: int, items: [SyncSession]}
  
GET    /api/v1/admin/monitoring/statistics
  Response: {
    records_by_status: {pending: int, approved: int, rejected: int},
    users_by_role: {admin: int, enumerator: int, supervisor: int, qa_officer: int}
  }

# Audit Log
GET    /api/v1/admin/audit-log
  Query: ?page=1&page_size=50&user_id=uuid&operation=create_user&date_from=iso&date_to=iso
  Response: {total: int, page: int, items: [AuditLog]}
```

#### QA API Endpoints

```
# Record Management
GET    /api/v1/qa/records
  Query: ?page=1&page_size=50&status=pending&lga=Lagos&ward=Ward1&enumerator=username&date_from=iso&date_to=iso&entity_type=building
  Response: {total: int, page: int, items: [Record]}
  
GET    /api/v1/qa/records/{id}
  Response: {
    id: uuid,
    entity_type: str,
    data: {...},
    photos: [Photo],
    geometry: GeoJSON,
    status: str,
    enumerator: User,
    submitted_at: str,
    reviewed_by?: User,
    reviewed_at?: str,
    rejection_reason?: str
  }
  
POST   /api/v1/qa/records/{id}/approve
  Response: {status: str, approved_at: str}
  
POST   /api/v1/qa/records/{id}/reject
  Request: {reason: str}
  Response: {status: str, rejected_at: str}
  
GET    /api/v1/qa/records/{id}/audit
  Response: [{timestamp: str, user: str, action: str, changes: {...}}]

# Statistics
GET    /api/v1/qa/statistics
  Query: ?lga=Lagos&ward=Ward1&date_from=iso&date_to=iso
  Response: {
    total_records: int,
    pending_records: int,
    approved_records: int,
    rejected_records: int,
    approval_rate_by_enumerator: {username: float},
    average_review_time_seconds: float,
    daily_volumes: [{date: str, submitted: int, reviewed: int}]
  }
  
GET    /api/v1/qa/flagged
  Query: ?flag_type=boundary&page=1&page_size=50
  Response: {total: int, items: [Record]}
```

### Service Layer Interfaces

#### UserService

```python
class UserService:
    async def create_user(
        db: AsyncSession,
        username: str,
        email: str,
        password: str,
        role_id: int,
        lga_assignment: list[str] | None,
        created_by: UUID
    ) -> User
    
    async def update_user(
        db: AsyncSession,
        user_id: UUID,
        role_id: int | None,
        lga_assignment: list[str] | None,
        locked: bool | None,
        updated_by: UUID
    ) -> User
    
    async def reset_password(
        db: AsyncSession,
        user_id: UUID,
        new_password: str,
        reset_by: UUID
    ) -> None
    
    async def list_users(
        db: AsyncSession,
        page: int,
        page_size: int
    ) -> tuple[int, list[User]]
    
    async def deactivate_user(
        db: AsyncSession,
        user_id: UUID,
        deactivated_by: UUID
    ) -> None
```

#### QAService

```python
class QAService:
    async def list_records(
        db: AsyncSession,
        page: int,
        page_size: int,
        filters: RecordFilters
    ) -> tuple[int, list[Record]]
    
    async def get_record_detail(
        db: AsyncSession,
        record_id: UUID
    ) -> RecordDetail
    
    async def approve_record(
        db: AsyncSession,
        record_id: UUID,
        approved_by: UUID
    ) -> None
    
    async def reject_record(
        db: AsyncSession,
        record_id: UUID,
        reason: str,
        rejected_by: UUID
    ) -> None
    
    async def get_statistics(
        db: AsyncSession,
        filters: StatisticsFilters
    ) -> QAStatistics
    
    async def get_audit_trail(
        db: AsyncSession,
        record_id: UUID
    ) -> list[AuditEntry]
```

#### ExportService

```python
class ExportService:
    async def create_export_task(
        db: AsyncSession,
        format: ExportFormat,
        entity_type: EntityType,
        filters: ExportFilters,
        created_by: UUID
    ) -> UUID  # task_id
    
    async def get_export_status(
        db: AsyncSession,
        task_id: UUID
    ) -> ExportStatus
    
    async def generate_csv_export(
        db: AsyncSession,
        entity_type: EntityType,
        filters: ExportFilters
    ) -> bytes
    
    async def generate_geojson_export(
        db: AsyncSession,
        entity_type: EntityType,
        filters: ExportFilters
    ) -> bytes
```

## Data Models

### Existing Models (No Changes Required)

The following existing models support the dashboard functionality:

- `User`: User accounts with role_id, lga_assignment, locked_at
- `Role`: Role definitions (admin, enumerator, supervisor, qa_officer)
- `Building`: Building enumeration records with verification_status, reviewed_by, reviewed_at, rejection_reason
- `Street`: Street enumeration records with verification_status
- `Photo`: Photo attachments linked to records
- `AuditLog`: System audit trail
- `SyncSession`: Mobile sync session logs
- `ShapefileVersion`: Shapefile version tracking
- `DropdownConfig`: Dropdown configuration options

### New Models

#### ExportTask

Tracks asynchronous export generation:

```python
class ExportTask(Base):
    __tablename__ = "export_tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    format: Mapped[str] = mapped_column(Text, nullable=False)  # csv, geojson
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)  # building, street, audit_log
    filters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")  # pending, processing, completed, failed
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

### Database Schema Changes

A new Alembic migration will be created to add the `export_tasks` table:

```sql
CREATE TABLE export_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID NOT NULL REFERENCES users(id),
    format TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    filters JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    file_path TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_export_tasks_created_by ON export_tasks(created_by);
CREATE INDEX idx_export_tasks_status ON export_tasks(status);
CREATE INDEX idx_export_tasks_created_at ON export_tasks(created_at DESC);
```

### Enhanced Audit Logging

The existing `AuditLog` model will be used to track all admin and QA actions:

- User creation/modification/deactivation
- Role changes
- Dropdown configuration changes
- Shapefile uploads
- Record approvals/rejections
- Export requests

## 
Implementation Details

### Frontend Implementation

#### Template Structure

```
feva-backend/app/templates/
├── base.html                 # Base template with common layout
├── admin/
│   ├── layout.html          # Admin dashboard layout
│   ├── index.html           # Dashboard home
│   ├── users.html           # User management
│   ├── roles.html           # Role management
│   ├── config.html          # System configuration
│   ├── shapefiles.html      # Shapefile management
│   ├── export.html          # Data export
│   ├── monitoring.html      # System monitoring
│   └── audit.html           # Audit log viewer
└── qa/
    ├── layout.html          # QA dashboard layout
    ├── index.html           # Dashboard home
    ├── records.html         # Record list
    ├── record_detail.html   # Record detail view
    ├── reports.html         # QA reports
    └── flagged.html         # Flagged records
```

#### JavaScript Modules

```
feva-backend/app/static/js/
├── common.js                # Shared utilities (AJAX, notifications)
├── admin/
│   ├── users.js            # User management interactions
│   ├── config.js           # Configuration editor
│   ├── shapefiles.js       # Shapefile upload handling
│   ├── export.js           # Export task management
│   └── monitoring.js       # Real-time monitoring updates
└── qa/
    ├── records.js          # Record list filtering and pagination
    ├── record_detail.js    # Record detail interactions
    └── reports.js          # Report generation
```

#### CSS Structure

```
feva-backend/app/static/css/
├── base.css                # Base styles and variables
├── admin.css               # Admin dashboard styles
└── qa.css                  # QA dashboard styles
```

### Backend Implementation

#### Route Handlers

**Admin Routes** (`feva-backend/app/api/dashboard_admin.py`):

```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(require_role("admin"))
):
    return templates.TemplateResponse(
        "admin/index.html",
        {"request": request, "user": current_user}
    )

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    current_user: User = Depends(require_role("admin"))
):
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "user": current_user}
    )

# Additional admin routes...
```

**QA Routes** (`feva-backend/app/api/dashboard_qa.py`):

```python
@router.get("/qa/", response_class=HTMLResponse)
async def qa_dashboard(
    request: Request,
    current_user: User = Depends(require_role("qa_officer", "admin"))
):
    return templates.TemplateResponse(
        "qa/index.html",
        {"request": request, "user": current_user}
    )

@router.get("/qa/records", response_class=HTMLResponse)
async def qa_records(
    request: Request,
    current_user: User = Depends(require_role("qa_officer", "admin"))
):
    return templates.TemplateResponse(
        "qa/records.html",
        {"request": request, "user": current_user}
    )

# Additional QA routes...
```

#### Service Implementation

**UserService** (`feva-backend/app/services/user_service.py`):

```python
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.user import User


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    role_id: int,
    lga_assignment: list[str] | None,
    created_by: UUID,
) -> User:
    """Create a new user account."""
    # Check username uniqueness
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise ValueError("Username already exists")
    
    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise ValueError("Email already exists")
    
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role_id=role_id,
        lga_assignment=lga_assignment,
    )
    db.add(user)
    await db.flush()
    
    # Audit log
    audit = AuditLog(
        user_id=created_by,
        operation="create_user",
        entity_type="user",
        entity_id=str(user.id),
        detail={"username": username, "role_id": role_id},
    )
    db.add(audit)
    await db.commit()
    
    return user


async def update_user(
    db: AsyncSession,
    user_id: UUID,
    role_id: int | None,
    lga_assignment: list[str] | None,
    locked: bool | None,
    updated_by: UUID,
) -> User:
    """Update user account details."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    
    changes = {}
    if role_id is not None and user.role_id != role_id:
        changes["role_id"] = {"old": user.role_id, "new": role_id}
        user.role_id = role_id
    
    if lga_assignment is not None and user.lga_assignment != lga_assignment:
        changes["lga_assignment"] = {"old": user.lga_assignment, "new": lga_assignment}
        user.lga_assignment = lga_assignment
    
    if locked is not None:
        if locked and not user.locked_at:
            user.locked_at = datetime.now(timezone.utc)
            changes["locked"] = True
        elif not locked and user.locked_at:
            user.locked_at = None
            changes["locked"] = False
    
    db.add(user)
    await db.flush()
    
    # Audit log
    if changes:
        audit = AuditLog(
            user_id=updated_by,
            operation="update_user",
            entity_type="user",
            entity_id=str(user_id),
            detail=changes,
        )
        db.add(audit)
    
    await db.commit()
    return user


async def reset_password(
    db: AsyncSession,
    user_id: UUID,
    new_password: str,
    reset_by: UUID,
) -> None:
    """Reset user password."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    
    user.password_hash = hash_password(new_password)
    user.failed_attempts = 0
    user.locked_at = None
    db.add(user)
    await db.flush()
    
    # Audit log
    audit = AuditLog(
        user_id=reset_by,
        operation="reset_password",
        entity_type="user",
        entity_id=str(user_id),
    )
    db.add(audit)
    await db.commit()


async def list_users(
    db: AsyncSession,
    page: int,
    page_size: int,
) -> tuple[int, list[User]]:
    """List all users with pagination."""
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar() or 0
    
    # Get paginated results
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    users = result.scalars().all()
    
    return total, list(users)


async def deactivate_user(
    db: AsyncSession,
    user_id: UUID,
    deactivated_by: UUID,
) -> None:
    """Deactivate a user account (soft delete)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    
    user.locked_at = datetime.now(timezone.utc)
    db.add(user)
    await db.flush()
    
    # Audit log
    audit = AuditLog(
        user_id=deactivated_by,
        operation="deactivate_user",
        entity_type="user",
        entity_id=str(user_id),
    )
    db.add(audit)
    await db.commit()
```

**QAService Extensions** (`feva-backend/app/services/qa_service.py`):

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.building import Building
from app.models.photo import Photo
from app.models.street import Street
from app.models.user import User


@dataclass
class RecordFilters:
    status: str | None = None
    lga: str | None = None
    ward: str | None = None
    enumerator: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    entity_type: str | None = None  # building, street, or None for both


@dataclass
class RecordSummary:
    id: UUID
    entity_type: str
    record_id: str
    lga: str
    ward: str | None
    enumerator_username: str
    submitted_at: datetime
    status: str


@dataclass
class RecordDetail:
    id: UUID
    entity_type: str
    data: dict
    photos: list[Photo]
    geometry: dict
    status: str
    enumerator: User
    submitted_at: datetime
    reviewed_by: User | None
    reviewed_at: datetime | None
    rejection_reason: str | None


async def list_records(
    db: AsyncSession,
    page: int,
    page_size: int,
    filters: RecordFilters,
) -> tuple[int, list[RecordSummary]]:
    """List records with filtering and pagination."""
    records = []
    
    # Query buildings
    if filters.entity_type in (None, "building"):
        building_query = select(Building)
        conditions = []
        
        if filters.status:
            conditions.append(Building.verification_status == filters.status)
        if filters.lga:
            conditions.append(Building.lga == filters.lga)
        if filters.ward:
            conditions.append(Building.ward == filters.ward)
        if filters.date_from:
            conditions.append(Building.enumeration_date >= filters.date_from)
        if filters.date_to:
            conditions.append(Building.enumeration_date <= filters.date_to)
        
        if conditions:
            building_query = building_query.where(and_(*conditions))
        
        building_result = await db.execute(building_query)
        buildings = building_result.scalars().all()
        
        for b in buildings:
            # Get enumerator username
            enum_result = await db.execute(select(User).where(User.id == b.enumerator_id))
            enumerator = enum_result.scalar_one()
            
            if filters.enumerator and enumerator.username != filters.enumerator:
                continue
            
            records.append(RecordSummary(
                id=b.id,
                entity_type="building",
                record_id=b.building_id,
                lga=b.lga,
                ward=b.ward,
                enumerator_username=enumerator.username,
                submitted_at=b.enumeration_date,
                status=b.verification_status,
            ))
    
    # Query streets
    if filters.entity_type in (None, "street"):
        street_query = select(Street)
        conditions = []
        
        if filters.status:
            conditions.append(Street.verification_status == filters.status)
        if filters.lga:
            conditions.append(Street.lga == filters.lga)
        if filters.ward:
            conditions.append(Street.ward == filters.ward)
        if filters.date_from:
            conditions.append(Street.enumeration_date >= filters.date_from)
        if filters.date_to:
            conditions.append(Street.enumeration_date <= filters.date_to)
        
        if conditions:
            street_query = street_query.where(and_(*conditions))
        
        street_result = await db.execute(street_query)
        streets = street_result.scalars().all()
        
        for s in streets:
            # Get enumerator username
            enum_result = await db.execute(select(User).where(User.id == s.enumerator_id))
            enumerator = enum_result.scalar_one()
            
            if filters.enumerator and enumerator.username != filters.enumerator:
                continue
            
            records.append(RecordSummary(
                id=s.id,
                entity_type="street",
                record_id=s.street_id,
                lga=s.lga,
                ward=s.ward,
                enumerator_username=enumerator.username,
                submitted_at=s.enumeration_date,
                status=s.verification_status,
            ))
    
    # Sort by submission date descending
    records.sort(key=lambda r: r.submitted_at, reverse=True)
    
    # Paginate
    total = len(records)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = records[start:end]
    
    return total, paginated


async def get_record_detail(
    db: AsyncSession,
    record_id: UUID,
    entity_type: str,
) -> RecordDetail:
    """Get detailed information for a single record."""
    if entity_type == "building":
        result = await db.execute(select(Building).where(Building.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Building not found")
        
        # Get photos
        photo_result = await db.execute(
            select(Photo).where(Photo.building_id == record.building_id)
        )
        photos = list(photo_result.scalars().all())
        
        # Get enumerator
        enum_result = await db.execute(select(User).where(User.id == record.enumerator_id))
        enumerator = enum_result.scalar_one()
        
        # Get reviewer if exists
        reviewer = None
        if record.reviewed_by:
            reviewer_result = await db.execute(select(User).where(User.id == record.reviewed_by))
            reviewer = reviewer_result.scalar_one_or_none()
        
        # Convert geometry to GeoJSON
        from geoalchemy2.shape import to_shape
        point = to_shape(record.geom)
        geometry = {"type": "Point", "coordinates": [point.x, point.y]}
        
        # Build data dict
        data = {
            "building_id": record.building_id,
            "street_id": record.street_id,
            "building_type": record.building_type,
            "number_of_floors": record.number_of_floors,
            "number_of_units": record.number_of_units,
            "building_condition": record.building_condition,
            "has_signage": record.has_signage,
            "business_names": record.business_names,
            "notes": record.notes,
            "lga": record.lga,
            "ward": record.ward,
            "postcode": record.postcode,
            "postcode_status": record.postcode_status,
            "gps_accuracy_m": float(record.gps_accuracy_m),
            "boundary_flag": record.boundary_flag,
            "duplicate_flag": record.duplicate_flag,
            "qa_flags": record.qa_flags,
        }
        
        return RecordDetail(
            id=record.id,
            entity_type="building",
            data=data,
            photos=photos,
            geometry=geometry,
            status=record.verification_status,
            enumerator=enumerator,
            submitted_at=record.enumeration_date,
            reviewed_by=reviewer,
            reviewed_at=record.reviewed_at,
            rejection_reason=record.rejection_reason,
        )
    
    elif entity_type == "street":
        result = await db.execute(select(Street).where(Street.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Street not found")
        
        # Get photos
        photo_result = await db.execute(
            select(Photo).where(Photo.street_id == record.street_id)
        )
        photos = list(photo_result.scalars().all())
        
        # Get enumerator
        enum_result = await db.execute(select(User).where(User.id == record.enumerator_id))
        enumerator = enum_result.scalar_one()
        
        # Get reviewer if exists
        reviewer = None
        if record.reviewed_by:
            reviewer_result = await db.execute(select(User).where(User.id == record.reviewed_by))
            reviewer = reviewer_result.scalar_one_or_none()
        
        # Convert geometry to GeoJSON
        from geoalchemy2.shape import to_shape
        linestring = to_shape(record.geom)
        geometry = {
            "type": "LineString",
            "coordinates": [[p[0], p[1]] for p in linestring.coords]
        }
        
        # Build data dict
        data = {
            "street_id": record.street_id,
            "street_name": record.street_name,
            "street_type": record.street_type,
            "surface_type": record.surface_type,
            "street_condition": record.street_condition,
            "has_drainage": record.has_drainage,
            "has_streetlights": record.has_streetlights,
            "notes": record.notes,
            "lga": record.lga,
            "ward": record.ward,
            "boundary_flag": record.boundary_flag,
            "qa_flags": record.qa_flags,
        }
        
        return RecordDetail(
            id=record.id,
            entity_type="street",
            data=data,
            photos=photos,
            geometry=geometry,
            status=record.verification_status,
            enumerator=enumerator,
            submitted_at=record.enumeration_date,
            reviewed_by=reviewer,
            reviewed_at=record.reviewed_at,
            rejection_reason=record.rejection_reason,
        )
    
    else:
        raise ValueError(f"Invalid entity_type: {entity_type}")


async def approve_record(
    db: AsyncSession,
    record_id: UUID,
    entity_type: str,
    approved_by: UUID,
) -> None:
    """Approve a record."""
    if entity_type == "building":
        result = await db.execute(select(Building).where(Building.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Building not found")
        
        if record.verification_status in ("approved", "rejected"):
            raise ValueError("Record already reviewed")
        
        record.verification_status = "approved"
        record.reviewed_by = approved_by
        record.reviewed_at = datetime.now(timezone.utc)
        db.add(record)
    
    elif entity_type == "street":
        result = await db.execute(select(Street).where(Street.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Street not found")
        
        if record.verification_status in ("approved", "rejected"):
            raise ValueError("Record already reviewed")
        
        record.verification_status = "approved"
        record.reviewed_by = approved_by
        record.reviewed_at = datetime.now(timezone.utc)
        db.add(record)
    
    else:
        raise ValueError(f"Invalid entity_type: {entity_type}")
    
    await db.flush()
    
    # Audit log
    audit = AuditLog(
        user_id=approved_by,
        operation="approve_record",
        entity_type=entity_type,
        entity_id=str(record_id),
    )
    db.add(audit)
    await db.commit()


async def reject_record(
    db: AsyncSession,
    record_id: UUID,
    entity_type: str,
    reason: str,
    rejected_by: UUID,
) -> None:
    """Reject a record with a reason."""
    if not reason or not reason.strip():
        raise ValueError("Rejection reason is required")
    
    if entity_type == "building":
        result = await db.execute(select(Building).where(Building.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Building not found")
        
        if record.verification_status in ("approved", "rejected"):
            raise ValueError("Record already reviewed")
        
        record.verification_status = "rejected"
        record.reviewed_by = rejected_by
        record.reviewed_at = datetime.now(timezone.utc)
        record.rejection_reason = reason
        db.add(record)
    
    elif entity_type == "street":
        result = await db.execute(select(Street).where(Street.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Street not found")
        
        if record.verification_status in ("approved", "rejected"):
            raise ValueError("Record already reviewed")
        
        record.verification_status = "rejected"
        record.reviewed_by = rejected_by
        record.reviewed_at = datetime.now(timezone.utc)
        record.rejection_reason = reason
        db.add(record)
    
    else:
        raise ValueError(f"Invalid entity_type: {entity_type}")
    
    await db.flush()
    
    # Audit log
    audit = AuditLog(
        user_id=rejected_by,
        operation="reject_record",
        entity_type=entity_type,
        entity_id=str(record_id),
        detail={"reason": reason},
    )
    db.add(audit)
    await db.commit()


async def get_audit_trail(
    db: AsyncSession,
    record_id: UUID,
    entity_type: str,
) -> list[dict]:
    """Get audit trail for a specific record."""
    result = await db.execute(
        select(AuditLog)
        .where(
            and_(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == str(record_id),
            )
        )
        .order_by(AuditLog.occurred_at.desc())
    )
    logs = result.scalars().all()
    
    trail = []
    for log in logs:
        # Get user info
        user = None
        if log.user_id:
            user_result = await db.execute(select(User).where(User.id == log.user_id))
            user = user_result.scalar_one_or_none()
        
        trail.append({
            "timestamp": log.occurred_at,
            "user": user.username if user else "system",
            "action": log.operation,
            "detail": log.detail,
        })
    
    return trail
```

### Security Implementation

#### Password Complexity Validation

```python
import re

def validate_password_complexity(password: str) -> tuple[bool, str]:
    """Validate password meets complexity requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    return True, ""
```

#### Rate Limiting

```python
from datetime import datetime, timedelta
from collections import defaultdict

# In-memory rate limiter (for production, use Redis)
_login_attempts: dict[str, list[datetime]] = defaultdict(list)

def check_rate_limit(username: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
    """Check if login attempts exceed rate limit."""
    now = datetime.now()
    cutoff = now - timedelta(minutes=window_minutes)
    
    # Remove old attempts
    _login_attempts[username] = [
        attempt for attempt in _login_attempts[username]
        if attempt > cutoff
    ]
    
    # Check limit
    if len(_login_attempts[username]) >= max_attempts:
        return False
    
    # Record attempt
    _login_attempts[username].append(now)
    return True
```

#### Input Sanitization

```python
import bleach

def sanitize_html_input(text: str) -> str:
    """Sanitize user input to prevent XSS attacks."""
    return bleach.clean(text, tags=[], strip=True)

def sanitize_sql_input(text: str) -> str:
    """Sanitize input for SQL queries (SQLAlchemy handles this, but extra layer)."""
    # SQLAlchemy's parameterized queries handle SQL injection
    # This is just for extra validation
    dangerous_patterns = [";", "--", "/*", "*/", "xp_", "sp_"]
    for pattern in dangerous_patterns:
        if pattern in text.lower():
            raise ValueError(f"Invalid input: contains dangerous pattern '{pattern}'")
    return text
```

### File Upload Security

```python
import hashlib
import magic
from pathlib import Path

ALLOWED_EXTENSIONS = {".zip"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def validate_file_upload(filename: str, content: bytes) -> tuple[bool, str]:
    """Validate uploaded file."""
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Allowed types: {ALLOWED_EXTENSIONS}"
    
    # Check size
    if len(content) > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
    
    # Check MIME type
    mime = magic.from_buffer(content, mime=True)
    if mime not in ("application/zip", "application/x-zip-compressed"):
        return False, "File content does not match extension"
    
    return True, ""
```

### Session Management

```python
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.security import create_access_token, decode_token

SESSION_DURATION_HOURS = 8

def create_session_token(user_id: UUID, role: str) -> str:
    """Create a session token for authenticated user."""
    expires_delta = timedelta(hours=SESSION_DURATION_HOURS)
    token_data = {
        "sub": str(user_id),
        "role": role,
    }
    return create_access_token(token_data, expires_delta)

def validate_session_token(token: str) -> tuple[UUID | None, str | None]:
    """Validate session token and return user_id and role."""
    try:
        payload = decode_token(token)
        user_id = UUID(payload.get("sub"))
        role = payload.get("role")
        return user_id, role
    except Exception:
        return None, None
```

## 
Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Unauthenticated Access Redirects to Login

For any dashboard route (admin or QA), when accessed without a valid authentication token, the system should redirect to the login page with a 302 or 401 status.

**Validates: Requirements 1.2, 2.2**

### Property 2: Admin Routes Require Admin Role

For any admin route under `/admin/*` or `/api/v1/admin/*`, when accessed with a valid token for a non-admin role (qa_officer, enumerator, supervisor), the system should return a 403 Forbidden error.

**Validates: Requirements 1.4, 1.5, 18.7**

### Property 3: QA Routes Require QA or Admin Role

For any QA route under `/qa/*` or `/api/v1/qa/*`, when accessed with a valid token for an unauthorized role (enumerator, supervisor), the system should return a 403 Forbidden error.

**Validates: Requirements 2.5, 19.7**

### Property 4: Valid Login Generates JWT with Role

For any valid username and password combination, the login endpoint should return a JWT token that, when decoded, contains the user's role information.

**Validates: Requirements 3.2**

### Property 5: Invalid Credentials Return 401

For any invalid username or password combination, the login endpoint should return a 401 Unauthorized error without revealing whether the username or password was incorrect.

**Validates: Requirements 3.3**

### Property 6: JWT Tokens Expire After 8 Hours

For any JWT token created by the system, the token's expiration claim should be set to 8 hours from the creation time.

**Validates: Requirements 3.4**

### Property 7: Expired Tokens Are Rejected

For any expired JWT token, when used to access a protected route, the system should return a 401 Unauthorized error and require re-authentication.

**Validates: Requirements 3.5, 16.3**

### Property 8: Post-Login Redirect Based on Role

For any successful login, the system should redirect the user to `/admin/` if their role is admin, or to `/qa/` if their role is qa_officer.

**Validates: Requirements 3.6**

### Property 9: User Creation Requires Unique Username

For any user creation request, if the username already exists in the system, the operation should fail with a validation error.

**Validates: Requirements 4.7**

### Property 10: User Management Operations Are Audited

For any user management operation (create, update, deactivate, password reset), the system should create an audit log entry with the operation type, target user ID, and the admin who performed the action.

**Validates: Requirements 4.6**

### Property 11: Role Changes Take Effect Immediately

For any user whose role is changed, subsequent authentication attempts should use the new role for authorization decisions.

**Validates: Requirements 5.4**

### Property 12: Dropdown Configuration Changes Are Audited

For any dropdown configuration operation (create, update, delete), the system should create an audit log entry with the operation type and the admin who performed the action.

**Validates: Requirements 6.5**

### Property 13: Empty Dropdown Values Are Rejected

For any dropdown configuration creation or update request, if the value or label field is empty or contains only whitespace, the operation should fail with a validation error.

**Validates: Requirements 6.6**

### Property 14: Shapefile Upload Validates File Format

For any file upload to the shapefile endpoint, if the file is not a valid ZIP archive or does not contain required shapefile components (.shp, .shx, .dbf), the operation should fail with a descriptive validation error.

**Validates: Requirements 7.2, 7.6**

### Property 15: Valid Shapefile Upload Creates Version Record

For any valid shapefile upload, the system should create a new ShapefileVersion record with a unique version number, upload timestamp, and the uploading admin's ID.

**Validates: Requirements 7.3**

### Property 16: Shapefile Geometry Stored in WKB Format

For any shapefile uploaded and processed, the geometry data stored in the boundary_zones table should be in WKB (Well-Known Binary) format.

**Validates: Requirements 7.7**

### Property 17: Export Requests Create Async Tasks

For any export request (CSV or GeoJSON), the system should create an ExportTask record with status "pending" and return a task ID immediately without blocking.

**Validates: Requirements 8.6**

### Property 18: Exports Include All Record Metadata

For any export of building or street records, the generated file should include all metadata fields including GPS coordinates, photo references, timestamps, enumerator information, and verification status.

**Validates: Requirements 8.7**

### Property 19: Record Filters Return Matching Records

For any record list request with filters (status, LGA, ward, enumerator, date range), all returned records should match all specified filter criteria.

**Validates: Requirements 10.2, 10.3, 10.4, 10.5**

### Property 20: Record Pagination Works for All Page Sizes

For any record list request with pagination parameters (page size of 10, 25, 50, or 100), the system should return exactly that many records (or fewer if on the last page) and provide accurate total count.

**Validates: Requirements 10.8**

### Property 21: Record Details Include All Required Fields

For any record detail request, the response should include all form fields, GPS coordinates with accuracy, associated photos, geometry data, submission timestamp, enumerator information, and current verification status.

**Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7**

### Property 22: Record Rejection Requires Comment

For any record rejection request, if the rejection reason is empty or contains only whitespace, the operation should fail with a validation error.

**Validates: Requirements 12.3**

### Property 23: Record Approval Updates Status and Metadata

For any record approval operation, the system should update the verification_status to "approved", set reviewed_by to the QA officer's ID, and set reviewed_at to the current timestamp.

**Validates: Requirements 12.4**

### Property 24: Record Rejection Updates Status and Stores Reason

For any record rejection operation, the system should update the verification_status to "rejected", set reviewed_by to the QA officer's ID, set reviewed_at to the current timestamp, and store the rejection reason.

**Validates: Requirements 12.5**

### Property 25: Review Actions Are Audited

For any record approval or rejection operation, the system should create an audit log entry with the operation type, record ID, entity type, and the QA officer who performed the action.

**Validates: Requirements 12.6**

### Property 26: Already-Reviewed Records Cannot Be Re-Reviewed

For any record with verification_status of "approved" or "rejected", attempts to approve or reject it again should fail with a validation error.

**Validates: Requirements 12.7**

### Property 27: Audit Trail Includes All Record Operations

For any record, the audit trail should include all operations performed on that record (creation, approval, rejection, status changes) with timestamps, user information, and operation details.

**Validates: Requirements 14.1, 14.3**

### Property 28: Audit Entries Include Required Fields

For any audit log entry, the record should include timestamp, user ID, operation type, entity type, and entity ID at minimum.

**Validates: Requirements 14.2**

### Property 29: Audit Trail Sorted Chronologically Descending

For any audit trail request, the returned entries should be sorted by timestamp in descending order (newest first).

**Validates: Requirements 14.4**

### Property 30: Token Refresh Within Valid Window

For any JWT token that is less than 7 hours old, when used to perform an authenticated action, the system should optionally issue a new token with extended expiration.

**Validates: Requirements 16.2**

### Property 31: Single Session Per User Account

For any user account, when a new login occurs, any existing active sessions for that user should be invalidated.

**Validates: Requirements 16.5**

### Property 32: API Endpoints Return Appropriate Status Codes

For any API request, the response status code should be appropriate for the outcome: 200 for success, 201 for creation, 400 for bad request, 401 for unauthorized, 403 for forbidden, 404 for not found, 500 for server error.

**Validates: Requirements 18.8, 19.8**

### Property 33: Input Validation Rejects Invalid Types

For any API request with parameters, if a parameter value does not match the expected type or format, the system should return a 400 Bad Request error with a descriptive message.

**Validates: Requirements 20.1**

### Property 34: SQL Injection Patterns Are Rejected

For any text input field, if the input contains SQL injection patterns (e.g., "; DROP TABLE", "' OR '1'='1"), the system should either sanitize the input or reject it with a validation error.

**Validates: Requirements 20.2**

### Property 35: XSS Patterns Are Sanitized

For any text input field, if the input contains XSS patterns (e.g., "<script>", "javascript:"), the system should sanitize the input by removing or escaping dangerous characters.

**Validates: Requirements 20.3**

### Property 36: Password Complexity Requirements Enforced

For any password creation or reset operation, if the password does not meet complexity requirements (minimum 8 characters, at least one uppercase, one lowercase, one number), the operation should fail with a descriptive validation error.

**Validates: Requirements 20.4**

### Property 37: Login Rate Limiting Enforced

For any username, if more than 5 failed login attempts occur within a 15-minute window, subsequent login attempts for that username should be blocked with a 429 Too Many Requests error.

**Validates: Requirements 20.5, 20.6**

### Property 38: File Upload Type Validation

For any file upload, if the file extension or MIME type is not in the allowed list (ZIP for shapefiles), the operation should fail with a validation error.

**Validates: Requirements 20.7**

### Property 39: File Upload Size Limit Enforced

For any file upload, if the file size exceeds 50MB, the operation should fail with a validation error before processing the file content.

**Validates: Requirements 20.8**

## Error Handling

### Error Response Format

All API errors should return a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    }
  }
}
```

### Error Categories

1. **Authentication Errors (401)**
   - Invalid credentials
   - Expired token
   - Missing token
   - Invalid token format

2. **Authorization Errors (403)**
   - Insufficient permissions
   - Role mismatch
   - Account locked

3. **Validation Errors (400)**
   - Missing required fields
   - Invalid field format
   - Duplicate values
   - Constraint violations

4. **Not Found Errors (404)**
   - User not found
   - Record not found
   - Resource not found

5. **Rate Limit Errors (429)**
   - Too many login attempts
   - API rate limit exceeded

6. **Server Errors (500)**
   - Database connection failure
   - Unexpected exceptions
   - File system errors

### Error Logging

All errors should be logged with:
- Timestamp
- Request ID
- User ID (if authenticated)
- Endpoint
- Error type and message
- Stack trace (for 500 errors)

### User-Facing Error Messages

Error messages should be:
- Clear and actionable
- Non-technical for end users
- Avoid exposing system internals
- Provide guidance on resolution

Examples:
- "Username already exists. Please choose a different username."
- "Invalid file format. Please upload a ZIP file containing shapefile components."
- "You do not have permission to access this resource."

## Testing Strategy

### Dual Testing Approach

This feature requires both unit testing and property-based testing for comprehensive coverage:

- **Unit Tests**: Verify specific examples, edge cases, and error conditions
- **Property Tests**: Verify universal properties across all inputs

### Unit Testing Focus

Unit tests should cover:

1. **Specific Examples**
   - Admin dashboard accessible at `/admin/`
   - QA dashboard accessible at `/qa/`
   - Login endpoint accepts username and password
   - Specific API endpoints exist and return expected structure

2. **Edge Cases**
   - Last admin user cannot be demoted or deleted
   - Empty dropdown values are rejected
   - Already-reviewed records cannot be re-reviewed

3. **Integration Points**
   - Authentication middleware integration
   - Database transaction handling
   - File upload processing
   - Async export task creation

4. **Error Conditions**
   - Invalid credentials return 401
   - Unauthorized access returns 403
   - Missing required fields return 400
   - Non-existent resources return 404

### Property-Based Testing Configuration

Property tests should use **Hypothesis** (Python) for the backend:

- **Minimum 100 iterations per test** to ensure comprehensive input coverage
- Each test must reference its design document property in a comment
- Tag format: `# Feature: admin-qa-dashboards, Property {number}: {property_text}`

### Property Testing Focus

Property tests should verify:

1. **Authentication and Authorization**
   - Property 1: Unauthenticated access redirects
   - Property 2: Admin routes require admin role
   - Property 3: QA routes require QA or admin role
   - Property 4: Valid login generates JWT with role
   - Property 5: Invalid credentials return 401
   - Property 7: Expired tokens are rejected

2. **User Management**
   - Property 9: Username uniqueness enforced
   - Property 10: User operations are audited
   - Property 11: Role changes take effect immediately

3. **Data Validation**
   - Property 13: Empty dropdown values rejected
   - Property 14: Shapefile format validation
   - Property 22: Rejection requires comment
   - Property 33: Input type validation
   - Property 36: Password complexity enforced

4. **Record Management**
   - Property 19: Filters return matching records
   - Property 20: Pagination works for all page sizes
   - Property 21: Record details include all fields
   - Property 23: Approval updates status and metadata
   - Property 24: Rejection updates status and stores reason
   - Property 26: Already-reviewed records cannot be re-reviewed

5. **Security**
   - Property 34: SQL injection patterns rejected
   - Property 35: XSS patterns sanitized
   - Property 37: Login rate limiting enforced
   - Property 38: File type validation
   - Property 39: File size limit enforced

6. **Audit Trail**
   - Property 25: Review actions are audited
   - Property 27: Audit trail includes all operations
   - Property 28: Audit entries include required fields
   - Property 29: Audit trail sorted chronologically

### Test Data Generation

For property-based tests, use Hypothesis strategies to generate:

- **Users**: Random usernames, emails, passwords, roles, LGA assignments
- **Records**: Random building and street data with various statuses
- **Filters**: Random combinations of status, LGA, ward, enumerator, date ranges
- **Tokens**: Valid and expired JWTs with various roles
- **Files**: Valid and invalid ZIP archives with various sizes
- **Inputs**: Valid and malicious text inputs (SQL injection, XSS patterns)

### Example Property Test

```python
from hypothesis import given, strategies as st
import pytest

# Feature: admin-qa-dashboards, Property 2: Admin routes require admin role
@given(
    role=st.sampled_from(["qa_officer", "enumerator", "supervisor"]),
    admin_route=st.sampled_from([
        "/admin/",
        "/admin/users",
        "/api/v1/admin/users",
        "/api/v1/admin/roles",
        "/api/v1/admin/dropdown-config",
    ])
)
@pytest.mark.property_test
def test_admin_routes_require_admin_role(client, role, admin_route):
    """For any admin route, non-admin roles should receive 403 Forbidden."""
    # Create user with non-admin role
    user = create_test_user(role=role)
    token = create_token_for_user(user)
    
    # Attempt to access admin route
    response = client.get(
        admin_route,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Should be forbidden
    assert response.status_code == 403
```

### Test Coverage Goals

- **Line Coverage**: Minimum 80% for all new code
- **Branch Coverage**: Minimum 75% for conditional logic
- **Property Coverage**: All 39 properties must have corresponding property tests
- **Integration Coverage**: All API endpoints must have integration tests

### Continuous Integration

Tests should run automatically on:
- Every pull request
- Every commit to main branch
- Nightly builds for extended property test runs (1000+ iterations)

## Implementation Phases

### Phase 1: Authentication and Authorization (Week 1)

1. Implement JWT token management with role claims
2. Create authentication middleware
3. Implement role-based authorization decorators
4. Add login/logout endpoints
5. Implement session management
6. Add rate limiting for login attempts
7. Write unit and property tests for auth

### Phase 2: Admin Dashboard Backend (Week 2)

1. Implement user management service and API endpoints
2. Implement role management API endpoints
3. Implement dropdown configuration service and API endpoints
4. Implement shapefile management (already exists, enhance if needed)
5. Implement monitoring endpoints
6. Implement audit log query endpoints
7. Write unit and property tests for admin APIs

### Phase 3: QA Dashboard Backend (Week 3)

1. Implement record listing service with filtering
2. Implement record detail retrieval
3. Implement approval/rejection operations
4. Implement QA statistics service
5. Implement audit trail retrieval
6. Write unit and property tests for QA APIs

### Phase 4: Export Functionality (Week 4)

1. Create ExportTask model and migration
2. Implement async export service
3. Implement CSV export generation
4. Implement GeoJSON export generation
5. Implement export task status tracking
6. Add background worker for export processing
7. Write unit and property tests for exports

### Phase 5: Frontend Implementation (Week 5-6)

1. Create base templates and layouts
2. Implement admin dashboard pages
3. Implement QA dashboard pages
4. Add JavaScript for AJAX interactions
5. Implement real-time updates (polling)
6. Add responsive CSS
7. Write frontend integration tests

### Phase 6: Security Hardening (Week 7)

1. Implement input sanitization
2. Add SQL injection prevention
3. Add XSS prevention
4. Implement file upload validation
5. Add CSRF protection
6. Conduct security audit
7. Write security-focused property tests

### Phase 7: Testing and Documentation (Week 8)

1. Complete all property tests
2. Achieve coverage goals
3. Conduct end-to-end testing
4. Write user documentation
5. Write API documentation
6. Conduct UAT with stakeholders
7. Address feedback and bugs

## Deployment Considerations

### Database Migrations

1. Create migration for export_tasks table
2. Ensure all existing users have valid roles
3. Add indexes for performance:
   - audit_log(entity_type, entity_id)
   - buildings(verification_status)
   - streets(verification_status)
   - export_tasks(status, created_at)

### Environment Configuration

Required environment variables:
- `JWT_PRIVATE_KEY`: RSA private key for token signing
- `JWT_PUBLIC_KEY`: RSA public key for token verification
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default 480 = 8 hours)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default 7)
- `MAX_LOGIN_ATTEMPTS`: Rate limit for login (default 5)
- `LOGIN_RATE_LIMIT_WINDOW_MINUTES`: Rate limit window (default 15)
- `MAX_UPLOAD_SIZE_MB`: File upload limit (default 50)

### Performance Optimization

1. Add database indexes for frequently queried fields
2. Implement query result caching for statistics
3. Use connection pooling for database
4. Optimize record listing queries with proper joins
5. Implement pagination for all list endpoints
6. Use async processing for exports

### Monitoring and Logging

1. Log all authentication attempts
2. Log all authorization failures
3. Log all user management operations
4. Log all record review operations
5. Monitor API response times
6. Monitor export task completion rates
7. Set up alerts for failed operations

### Backup and Recovery

1. Regular database backups (daily)
2. Backup export files before cleanup
3. Maintain audit log integrity
4. Document recovery procedures
5. Test backup restoration regularly

## Future Enhancements

1. **Advanced Filtering**: Add full-text search for records
2. **Bulk Operations**: Allow bulk approval/rejection of records
3. **Custom Reports**: Allow admins to create custom report templates
4. **Email Notifications**: Notify enumerators of rejections
5. **Dashboard Widgets**: Customizable dashboard layouts
6. **Export Scheduling**: Schedule recurring exports
7. **API Rate Limiting**: Implement per-user API rate limits
8. **Two-Factor Authentication**: Add 2FA for admin accounts
9. **Activity Dashboard**: Real-time activity feed
10. **Mobile App**: Native mobile apps for dashboards
