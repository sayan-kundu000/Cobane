from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

class ProjectStatsResponse(BaseModel):
    average_pylint_score: float = Field(..., description="Average Pylint checker rating")
    average_maintainability_index: float = Field(..., description="Average Radon maintainability index rating")
    total_bandit_vulnerabilities: int = Field(..., description="Aggregate count of security warnings")
    total_reviews_conducted: int = Field(..., description="Total reviews run on this project")

    model_config = ConfigDict(from_attributes=True)
