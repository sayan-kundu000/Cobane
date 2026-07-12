from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    project_id: int


class ReviewCreate(ReviewBase):
    uploaded_source_id: Optional[int] = Field(
        default=None, description="Uploaded source ID to review. If omitted, uses latest."
    )


class ReviewFindingResponse(BaseModel):
    id: int
    review_id: int
    file_path: str
    line_number: int
    severity: str
    category: str
    message: str
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    provider: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewMetricsResponse(BaseModel):
    id: int
    review_id: int
    cyclomatic_complexity: int
    maintainability_index: float
    loc: int
    functions_count: int
    classes_count: int

    model_config = ConfigDict(from_attributes=True)


class ReportResponse(BaseModel):
    id: int
    review_id: int
    format: str
    file_path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewDetailResponse(ReviewBase):
    id: int
    uploaded_source_id: int
    status: str
    pylint_score: Optional[float] = None
    radon_mi_score: Optional[float] = None
    bandit_issues_count: Optional[int] = None
    ai_review_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewResponse(ReviewBase):
    id: int
    status: str = "pending"
    pylint_score: Optional[float] = None
    radon_mi_score: Optional[float] = None
    bandit_issues_count: Optional[int] = None
    ai_review_completed: bool = False

    static_analysis_report: Optional[Dict[str, Any]] = None
    ai_suggestions: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
