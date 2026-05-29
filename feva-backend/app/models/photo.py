import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    photo_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    record_type: Mapped[str] = mapped_column(Text, nullable=False)
    record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    is_frontage: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    geom: Mapped[str | None] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    captured_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    synced_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
