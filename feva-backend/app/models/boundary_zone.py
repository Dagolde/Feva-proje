"""BoundaryZone model — server-side storage for ingested shapefile polygons."""
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class BoundaryZone(Base):
    __tablename__ = "boundary_zones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    zone_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    zone_name: Mapped[str] = mapped_column(Text, nullable=False)
    zone_type: Mapped[str] = mapped_column(Text, nullable=False)  # lga/ward/nipost/admin
    lga_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    ward_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    postcode: Mapped[str | None] = mapped_column(Text, nullable=True)
    geom: Mapped[str] = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
    shapefile_version: Mapped[str] = mapped_column(Text, nullable=False)
    shapefile_version_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("shapefile_versions.id"), nullable=True
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
