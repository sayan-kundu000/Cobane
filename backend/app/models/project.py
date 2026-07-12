from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.review import Review


class Project(Base, BaseModel):
    """Database model representing reviewable target workspaces."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="projects")
    uploaded_sources: Mapped[List["UploadedSource"]] = relationship(
        "UploadedSource", back_populates="project", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="project", cascade="all, delete-orphan")


class UploadedSource(Base, BaseModel):
    """Database model mapping uploaded codebase file attachments."""

    __tablename__ = "uploaded_sources"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processed, error

    project: Mapped["Project"] = relationship("Project", back_populates="uploaded_sources")
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="uploaded_source", cascade="all, delete-orphan"
    )
