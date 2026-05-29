import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Street(Base):
    __tablename__ = "streets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    street_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    street_name: Mapped[str] = mapped_column(Text, nullable=False)
    street_address: Mapped[str] = mapped_column(Text, nullable=False, default="")
    street_type: Mapped[str] = mapped_column(Text, nullable=False)
    surface_type: Mapped[str] = mapped_column(Text, nullable=False)
    street_condition: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    geom: Mapped[str] = mapped_column(Geometry("LINESTRING", srid=4326), nullable=False)
    zone: Mapped[str | None] = mapped_column(Text, nullable=True)
    lga: Mapped[str] = mapped_column(Text, nullable=False)
    ward: Mapped[str | None] = mapped_column(Text, nullable=True)
    enumerator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    enumeration_date: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    verification_status: Mapped[str] = mapped_column(
        Text, nullable=False, default="pending"
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    boundary_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    gps_accuracy_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    qa_flags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    device_local_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    device_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    synced_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
