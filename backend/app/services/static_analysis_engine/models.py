from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class NormalizedFinding(BaseModel):
    """Unified schema representing a static code analyzer warning or issue."""

    analyzer: str = Field(..., description="Static checker tool identifier (pylint, bandit, etc.)")
    category: str = Field(..., description="Warning type: style, security, complexity, performance, syntax, etc.")
    severity: str = Field(..., description="Mapped standard rating: info, low, medium, high, critical")
    rule: str = Field(..., description="Tool warning rule identifier key or code name (e.g. C0114, B101)")
    description: str = Field(..., description="Detailed textual message context detailing the warning details")
    recommendation: Optional[str] = Field(
        None, description="Actionable suggestion detailing how to address the warning"
    )
    file_path: str = Field(..., description="Codebase relative path file containing the warning")
    function_name: Optional[str] = Field(None, description="Optional method or function scope containing the issue")
    line_number: int = Field(..., ge=1, description="1-indexed line number containing the issue")
    confidence: str = Field(
        default="medium", description="Accuracy confidence level classification (low, medium, high)"
    )

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class NormalizedMetrics(BaseModel):
    """Unified schema mapping Radon code metrics and line counts."""

    cyclomatic_complexity: int = Field(default=0, description="Highest cyclomatic complexity score detected")
    maintainability_index: float = Field(default=100.0, description="Radon maintainability index score (0 to 100)")
    loc: int = Field(default=0, description="Lines of Code (LOC)")
    functions_count: int = Field(default=0, description="Total count of functions mapped")
    classes_count: int = Field(default=0, description="Total count of classes mapped")

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class StaticAnalysisReport(BaseModel):
    """Consolidated static analysis report aggregates housing parsed findings, metrics, and tool scores."""

    findings: List[NormalizedFinding] = Field(
        default_factory=list, description="Aggregated lists of parsed static issues"
    )
    metrics: NormalizedMetrics = Field(default_factory=NormalizedMetrics, description="Aggregated complexity metrics")
    pylint_score: Optional[float] = Field(None, description="Overall Pylint checker rating (0.0 to 10.0)")
    radon_mi_score: Optional[float] = Field(None, description="Module average maintainability index")
    bandit_issues_count: Optional[int] = Field(None, description="Total security warnings count")

    model_config = ConfigDict(from_attributes=True, extra="ignore")
