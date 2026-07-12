from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, BaseModel

if TYPE_CHECKING:
    from app.models.project import Project, UploadedSource


class Review(Base, BaseModel):
    """Database model mapping complete AI and static code runs."""

    __tablename__ = "reviews"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    uploaded_source_id: Mapped[int] = mapped_column(
        ForeignKey("uploaded_sources.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, completed, failed
    pylint_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    radon_mi_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bandit_issues_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_review_completed: Mapped[bool] = mapped_column(default=False)

    project: Mapped["Project"] = relationship("Project", back_populates="reviews")
    uploaded_source: Mapped["UploadedSource"] = relationship("UploadedSource", back_populates="reviews")
    findings: Mapped[List["ReviewFinding"]] = relationship(
        "ReviewFinding", back_populates="review", cascade="all, delete-orphan"
    )
    metrics: Mapped[Optional["ReviewMetrics"]] = relationship(
        "ReviewMetrics", back_populates="review", uselist=False, cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="review", cascade="all, delete-orphan")


class ReviewFinding(Base, BaseModel):
    """Database model storing granular static checker warnings and AI advice details."""

    __tablename__ = "review_findings"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # info, warning, error, critical
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # security, style, complexity, performance
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    code_snippet: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    suggestion: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    provider: Mapped[str] = mapped_column(String(50))  # pylint, bandit, radon, ai

    review: Mapped["Review"] = relationship("Review", back_populates="findings")


class ReviewMetrics(Base, BaseModel):
    """Database model storing complexity aggregations."""

    __tablename__ = "review_metrics"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), unique=True, nullable=False)
    cyclomatic_complexity: Mapped[int] = mapped_column(Integer, default=0)
    maintainability_index: Mapped[float] = mapped_column(Float, default=100.0)
    loc: Mapped[int] = mapped_column(Integer, default=0)
    functions_count: Mapped[int] = mapped_column(Integer, default=0)
    classes_count: Mapped[int] = mapped_column(Integer, default=0)

    review: Mapped["Review"] = relationship("Review", back_populates="metrics")


class Report(Base, BaseModel):
    """Database model tracking exported PDF, HTML, or Markdown summaries."""

    __tablename__ = "reports"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    format: Mapped[str] = mapped_column(String(10), nullable=False)  # pdf, html, md
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    review: Mapped["Review"] = relationship("Review", back_populates="reports")
