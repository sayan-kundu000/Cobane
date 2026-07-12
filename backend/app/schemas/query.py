from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pydantic model representing pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    model_config = ConfigDict(extra="ignore")

    @property
    def skip(self) -> int:
        """Offset to skip in SQL query."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Limit count in SQL query."""
        return self.page_size


class SortParams(BaseModel):
    """Pydantic model representing sorting query parameters."""

    sort_by: str = Field(default="id", description="Field to sort by")
    ascending: bool = Field(default=True, description="True for ascending, False for descending")

    model_config = ConfigDict(extra="ignore")

    @property
    def order_by_clause(self) -> str:
        """Helper to generate text sorting identifier."""
        return self.sort_by if self.ascending else f"-{self.sort_by}"


class FilterParams(BaseModel):
    """Pydantic model representing filtering query parameters."""

    owner_id: Optional[int] = Field(default=None, description="Filter by owner user ID")
    project_id: Optional[int] = Field(default=None, description="Filter by project ID")
    language: Optional[str] = Field(default=None, description="Filter by code language")
    status: Optional[str] = Field(default=None, description="Filter by status")
    severity: Optional[str] = Field(default=None, description="Filter by severity level")
    min_score: Optional[float] = Field(default=None, description="Filter by minimum score")
    max_score: Optional[float] = Field(default=None, description="Filter by maximum score")
    start_date: Optional[datetime] = Field(default=None, description="Filter by items created after date")
    end_date: Optional[datetime] = Field(default=None, description="Filter by items created before date")

    model_config = ConfigDict(extra="ignore")


class SearchParams(BaseModel):
    """Pydantic model representing search keyword queries."""

    q: Optional[str] = Field(default=None, description="Search keyword query")

    model_config = ConfigDict(extra="ignore")


class QueryParams(BaseModel):
    """Aggregated query criteria including pagination, sorting, filters, and keyword search."""

    pagination: PaginationParams = Field(default_factory=PaginationParams)
    sort: SortParams = Field(default_factory=SortParams)
    filters: FilterParams = Field(default_factory=FilterParams)
    search: SearchParams = Field(default_factory=SearchParams)

    model_config = ConfigDict(extra="ignore")


class PaginationMetadata(BaseModel):
    """Metadata response payload conveying result metrics."""

    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items returned in current page")
    total_items: int = Field(..., description="Total items available matching filters")
    total_pages: int = Field(..., description="Total pages available matching filters")

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized wrapper container housing paginated list responses and metadata."""

    items: List[T] = Field(..., description="List of items returned for the current page")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata information")

    model_config = ConfigDict(from_attributes=True)


def get_query_params(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="id", description="Field to sort by"),
    ascending: bool = Query(default=True, description="True for ascending, False for descending"),
    owner_id: Optional[int] = Query(default=None, description="Filter by owner user ID"),
    project_id: Optional[int] = Query(default=None, description="Filter by project ID"),
    language: Optional[str] = Query(default=None, description="Filter by code language"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    severity: Optional[str] = Query(default=None, description="Filter by severity level"),
    min_score: Optional[float] = Query(default=None, description="Filter by minimum score"),
    max_score: Optional[float] = Query(default=None, description="Filter by maximum score"),
    start_date: Optional[datetime] = Query(default=None, description="Filter by items created after date"),
    end_date: Optional[datetime] = Query(default=None, description="Filter by items created before date"),
    q: Optional[str] = Query(default=None, description="Search keyword query"),
) -> QueryParams:
    """FastAPI Dependency injector function constructing a clean QueryParams schema object."""
    return QueryParams(
        pagination=PaginationParams(page=page, page_size=page_size),
        sort=SortParams(sort_by=sort_by, ascending=ascending),
        filters=FilterParams(
            owner_id=owner_id,
            project_id=project_id,
            language=language,
            status=status,
            severity=severity,
            min_score=min_score,
            max_score=max_score,
            start_date=start_date,
            end_date=end_date,
        ),
        search=SearchParams(q=q),
    )
