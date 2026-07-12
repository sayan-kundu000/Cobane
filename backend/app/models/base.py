import uuid
from datetime import datetime
from sqlalchemy import MetaData, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.utils.datetime_helpers import get_utc_now

# Standard database naming conventions for indices and keys to ensure clean Alembic scripts
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Declarative Base Class incorporating custom metadata naming rules."""

    metadata = metadata


class BaseModel:
    """Abstract model class providing unified ID, UUID, and lifecycle timestamp attributes."""

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)
    is_active: Mapped[bool] = mapped_column(default=True)
