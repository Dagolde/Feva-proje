"""Celery application and beat schedule for FEVA background tasks.

Requirements: 14.4
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# ── Celery app ────────────────────────────────────────────────────────────────

celery_app = Celery(
    "feva",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# ── Beat schedule ─────────────────────────────────────────────────────────────

celery_app.conf.beat_schedule = {
    "monthly-export": {
        "task": "app.worker.run_monthly_export",
        # 1st of every month at 02:00 UTC (Requirement 14.4)
        "schedule": crontab(hour=2, minute=0, day_of_month=1),
    },
    "cleanup-old-exports": {
        "task": "app.worker.cleanup_old_exports",
        # Run daily at 03:00 UTC
        "schedule": crontab(hour=3, minute=0),
    },
}


# ── Tasks ─────────────────────────────────────────────────────────────────────

@celery_app.task(name="app.worker.run_monthly_export", bind=True, max_retries=3)
def run_monthly_export(self) -> dict:
    """Generate GeoJSON + Shapefile for all approved records in the previous month.

    Stores output in IGSL object storage.
    Requirements: 14.4
    """
    now = datetime.now(timezone.utc)
    # Previous month
    if now.month == 1:
        year, month = now.year - 1, 12
    else:
        year, month = now.year, now.month - 1

    try:
        return asyncio.run(_async_monthly_export(year, month))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * 5)  # retry after 5 min


@celery_app.task(name="app.worker.process_export_task", bind=True, max_retries=3)
def process_export_task(self, task_id: str) -> dict:
    """Process a pending export task created via the API.

    Updates the ExportTask record with status, file_path, or error_message.
    Requirements: 8.6
    """
    try:
        return asyncio.run(_async_process_export_task(task_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


async def _async_process_export_task(task_id: str) -> dict:
    """Async implementation: run the export and update the task record."""
    import uuid as _uuid

    from sqlalchemy import select, update
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.export_task import ExportTask
    from app.services.export_service import generate_csv_export, generate_geojson_export

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    task_uuid = _uuid.UUID(task_id)

    async with async_session() as session:
        result = await session.execute(select(ExportTask).where(ExportTask.id == task_uuid))
        task = result.scalar_one_or_none()

        if task is None:
            return {"error": f"Task {task_id} not found"}

        # Mark as processing
        await session.execute(
            update(ExportTask)
            .where(ExportTask.id == task_uuid)
            .values(status="processing")
        )
        await session.commit()

        try:
            if task.format == "csv":
                file_path = await generate_csv_export(session, task)
            elif task.format == "geojson":
                file_path = await generate_geojson_export(session, task)
            else:
                raise ValueError(f"Unsupported export format: {task.format}")

            await session.execute(
                update(ExportTask)
                .where(ExportTask.id == task_uuid)
                .values(status="completed", file_path=file_path)
            )
            await session.commit()
            return {"task_id": task_id, "status": "completed", "file_path": file_path}

        except Exception as exc:
            await session.execute(
                update(ExportTask)
                .where(ExportTask.id == task_uuid)
                .values(status="failed", error_message=str(exc))
            )
            await session.commit()
            raise

    await engine.dispose()


@celery_app.task(name="app.worker.cleanup_old_exports")
def cleanup_old_exports() -> dict:
    """Delete export files older than 7 days and mark tasks as expired.

    Requirements: 24.2
    """
    return asyncio.run(_async_cleanup_old_exports())


async def _async_cleanup_old_exports() -> dict:
    """Async implementation of export file cleanup."""
    import os
    from datetime import timedelta

    from sqlalchemy import select, update
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.export_task import ExportTask

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    deleted_files = 0
    expired_tasks = 0

    async with async_session() as session:
        result = await session.execute(
            select(ExportTask).where(
                ExportTask.status == "completed",
                ExportTask.created_at < cutoff,
                ExportTask.file_path.isnot(None),
            )
        )
        old_tasks = result.scalars().all()

        for task in old_tasks:
            if task.file_path and os.path.exists(task.file_path):
                try:
                    os.remove(task.file_path)
                    deleted_files += 1
                except OSError:
                    pass

            await session.execute(
                update(ExportTask)
                .where(ExportTask.id == task.id)
                .values(status="expired", file_path=None)
            )
            expired_tasks += 1

        await session.commit()

    await engine.dispose()
    return {"deleted_files": deleted_files, "expired_tasks": expired_tasks}


async def _async_monthly_export(year: int, month: int) -> dict:
    """Async implementation of the monthly export task."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    from app.services.export_service import (
        create_export_job,
        run_geojson_export,
        run_shapefile_export,
        generate_coverage_report_csv,
        generate_dq_metrics_snapshot_csv,
        _bundle_into_zip,
        EXPORT_DIR,
    )

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Use a system user ID for automated exports
    system_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    class _SystemUser:
        id = system_user_id

    async with async_session() as session:
        geojson_job_id = create_export_job("geojson_monthly", system_user_id)
        await run_geojson_export(session, geojson_job_id, _SystemUser(), year, month)

        shp_job_id = create_export_job("shapefile_monthly", system_user_id)
        await run_shapefile_export(session, shp_job_id, _SystemUser(), year, month)

        # Generate coverage report and DQ metrics snapshot (Requirements 22.1–22.3)
        coverage_csv = await generate_coverage_report_csv(session, year, month)
        dq_csv = await generate_dq_metrics_snapshot_csv(session, year, month)

        # Bundle both into a dedicated monthly package ZIP (Requirement 22.3)
        monthly_zip_bytes = _bundle_into_zip({
            "coverage_report.csv": coverage_csv,
            "dq_metrics_snapshot.csv": dq_csv,
        })
        monthly_zip_path = EXPORT_DIR / f"monthly_{year}_{month:02d}_reports.zip"
        monthly_zip_path.write_bytes(monthly_zip_bytes)

    await engine.dispose()

    return {
        "year": year,
        "month": month,
        "geojson_job_id": geojson_job_id,
        "shapefile_job_id": shp_job_id,
        "monthly_reports_zip": str(monthly_zip_path),
    }
