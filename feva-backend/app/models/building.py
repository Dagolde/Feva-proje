import uuid
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    building_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    street_id: Mapped[str] = mapped_column(
        Text, ForeignKey("streets.street_id"), nullable=False
    )
    building_type: Mapped[str] = mapped_column(Text, nullable=False)
    number_of_floors: Mapped[int] = mapped_column(Integer, nullable=False)
    number_of_units: Mapped[int] = mapped_column(Integer, nullable=False)
    building_condition: Mapped[str] = mapped_column(Text, nullable=False)
    street_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    has_signage: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    business_names: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    geom: Mapped[str] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    gps_accuracy_m: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    zone: Mapped[str | None] = mapped_column(Text, nullable=True)
    lga: Mapped[str] = mapped_column(Text, nullable=False)
    ward: Mapped[str | None] = mapped_column(Text, nullable=True)
    postcode: Mapped[str | None] = mapped_column(Text, nullable=True)
    postcode_status: Mapped[str] = mapped_column(Text, nullable=False, default="resolved")
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
    dispute_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    verified_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    boundary_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    gps_accuracy_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    duplicate_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    qa_flags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    qr_code_value: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
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
