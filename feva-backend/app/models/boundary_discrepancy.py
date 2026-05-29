"""BoundaryDiscrepancy model.

Requirements: 21.1, 21.2, 21.5, 21.6, 21.7
"""
from __future__ import annotations

import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class BoundaryDiscrepancy(Base):
    __tablename__ = "boundary_discrepancies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    postcode_polygon_id: Mapped[str] = mapped_column(Text, nullable=False)
    admin_polygon_id: Mapped[str] = mapped_column(Text, nullable=False)
    admin_type: Mapped[str] = mapped_column(Text, nullable=False)
    overlap_area_m2: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    shapefile_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("shapefile_versions.id", name="fk_boundary_discrepancies_shapefile_version_id"),
        nullable=True,
    )
    detected_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "admin_type IN ('lga','ward')",
            name="ck_boundary_discrepancies_admin_type",
        ),
    )
