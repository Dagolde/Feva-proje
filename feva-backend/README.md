# FEVA Backend

**Field Enumeration and Verification App — Python FastAPI Backend**

FEVA is an offline-first mobile data collection system commissioned by Inspired Global Systems Ltd (IGSL) on behalf of a Nigerian State Government as part of a statewide Addressing Infrastructure Programme.

## Overview

The FEVA backend provides the server-side API, data storage, and processing pipeline for the FEVA mobile app. It handles:

- JWT RS256 authentication with optional TOTP 2FA and account lockout
- Incremental sync upload from Enumerator devices (streets, buildings, photos)
- Server-side QA/QC validation (GPS precision, geometry type, mandatory fields, duplicate detection)
- Shapefile ingestion pipeline (GDAL/OGR → PostGIS → device distribution package)
- Supervisor spot-check and approval/rejection workflows
- Certified GeoJSON and ESRI Shapefile export (RFC 7946 compliant, round-trip verified)
- Immutable audit log (append-only, 24-month retention)
- QA dashboard with real-time metrics
- Admin user management and configurable dropdown values

## Tech Stack

- **Framework**: FastAPI (async, Python 3.11+)
- **Database**: PostgreSQL 15 + PostGIS 3
- **ORM**: SQLAlchemy (async) + GeoAlchemy2
- **Migrations**: Alembic
- **Auth**: python-jose (RS256 JWT), pyotp (TOTP), passlib (bcrypt)
- **Geospatial**: GDAL/OGR, Shapely, GeoPandas, Fiona
- **Task Queue**: Celery + Redis (monthly export jobs)
- **Testing**: pytest, pytest-asyncio, Hypothesis
- **Linting / Types**: ruff, mypy

## Getting Started

```bash
# Install dependencies
pip install -e ".[dev]"

# Start local services
docker-compose up -d

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

## Running Tests

```bash
pytest --cov=app tests/
```

## Branch Strategy

| Branch      | Purpose                          |
|-------------|----------------------------------|
| `main`      | Production releases only         |
| `develop`   | Integration branch for features  |
| `feature/*` | Individual feature branches      |
| `hotfix/*`  | Production hotfix branches       |

## Ownership

Maintained by [@igsl/feva-dev](https://github.com/orgs/igsl/teams/feva-dev).  
All source code and collected data are the property of IGSL and the commissioning State Government.  
No data is transmitted to third-party systems without explicit Admin authorisation (Requirement 20.3).
