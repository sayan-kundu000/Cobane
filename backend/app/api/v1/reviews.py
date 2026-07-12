from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.core.dependencies import get_db, get_current_user
from app.core.responses import StandardJSONResponse
from app.models.user import User
from app.schemas.review import (
    ReviewCreate,
    ReviewDetailResponse,
    ReviewFindingResponse,
    ReviewMetricsResponse,
    ReportResponse,
)
from app.schemas.query import QueryParams, get_query_params, PaginatedResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_class=StandardJSONResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_in: ReviewCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Triggers static analysis and AI reviews on a project uploaded source file version."""
    review = await ReviewService.create_review(db, review_in, current_user.id)
    return ReviewDetailResponse.model_validate(review)


@router.get("", response_class=StandardJSONResponse)
async def list_reviews(
    project_id: Optional[int] = Query(default=None, description="Optional filter by project ID scope"),
    params: QueryParams = Depends(get_query_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists reviews matching query params. Users can only query reviews of projects they own."""
    # Scoping checks if project_id is provided
    if project_id and not current_user.is_superuser:
        from app.services.project_service import ProjectService

        # Will raise Forbidden/NotFound if user doesn't own project
        await ProjectService.get_project(db, project_id, current_user.id)

    # Scoped reviews list
    reviews, total = await ReviewService.list_reviews(db, params, project_id=project_id)

    # Filter reviews by project ownership if not admin and not already project-filtered
    if not current_user.is_superuser and not project_id:
        # Filter in memory or scope by owner. Scoped query in repo checks owner via joins,
        # but to keep it simple and robust, let's join projects to filter by project owner!
        # Actually, let's write a helper or run list of user's project ids:
        from app.db.repositories.project_repository import ProjectRepository

        proj_repo = ProjectRepository(db)
        user_projects = await proj_repo.list_by_owner(current_user.id, limit=1000)
        user_proj_ids = {p.id for p in user_projects}

        # Re-query scoped by project ids or filter in memory
        reviews = [r for r in reviews if r.project_id in user_proj_ids]
        total = len(reviews)  # approximate total for in-memory

    total_pages = (total + params.pagination.page_size - 1) // params.pagination.page_size if total > 0 else 0
    items = [ReviewDetailResponse.model_validate(r) for r in reviews]

    return {
        "items": items,
        "pagination": {
            "page": params.pagination.page,
            "page_size": params.pagination.page_size,
            "total_items": total,
            "total_pages": total_pages,
        },
    }


@router.get("/{review_id}", response_class=StandardJSONResponse)
async def get_review(
    review_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieves metadata properties and checker summaries for a specific review run."""
    owner_scope = current_user.id if not current_user.is_superuser else 0
    # Superuser logic bypass:
    if current_user.is_superuser:
        from app.db.repositories.review_repository import ReviewRepository

        review_repo = ReviewRepository(db)
        review = await review_repo.get(review_id)
        if not review:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(f"Review with ID {review_id} not found.")
    else:
        review = await ReviewService.get_review(db, review_id, owner_scope)

    return ReviewDetailResponse.model_validate(review)


@router.delete("/{review_id}", response_class=StandardJSONResponse)
async def delete_review(
    review_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Removes a review run and all its findings/metrics records."""
    owner_scope = current_user.id if not current_user.is_superuser else 0
    if current_user.is_superuser:
        from app.db.repositories.review_repository import ReviewRepository

        review_repo = ReviewRepository(db)
        review = await review_repo.get(review_id)
        if not review:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(f"Review with ID {review_id} not found.")
        # retrieve project owner
        from app.models.project import Project

        res = await db.execute(select(Project).filter(Project.id == review.project_id))
        proj = res.scalars().first()
        owner_scope = proj.owner_id if proj else 0

    await ReviewService.delete_review(db, review_id, owner_scope)
    return {"message": "Review successfully deleted."}


@router.get("/{review_id}/findings", response_class=StandardJSONResponse)
async def get_review_findings(
    review_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieves all static checker and AI findings detected on a specific review run."""
    owner_scope = current_user.id if not current_user.is_superuser else 0
    if current_user.is_superuser:
        owner_scope = 0  # skip ownership check in get_findings by using a bypass if we write it.
        # Actually, let's verify review first:
        from app.db.repositories.review_repository import ReviewRepository

        review_repo = ReviewRepository(db)
        review = await review_repo.get(review_id)
        if not review:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(f"Review with ID {review_id} not found.")
        from app.models.project import Project

        res = await db.execute(select(Project).filter(Project.id == review.project_id))
        proj = res.scalars().first()
        owner_scope = proj.owner_id if proj else 0

    findings = await ReviewService.get_findings(db, review_id, owner_scope)
    return [ReviewFindingResponse.model_validate(f) for f in findings]


@router.get("/{review_id}/metrics", response_class=StandardJSONResponse)
async def get_review_metrics(
    review_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieves complexity metrics (LOC, CC, maintainability) for a specific review run."""
    owner_scope = current_user.id if not current_user.is_superuser else 0
    if current_user.is_superuser:
        from app.db.repositories.review_repository import ReviewRepository

        review_repo = ReviewRepository(db)
        review = await review_repo.get(review_id)
        if not review:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(f"Review with ID {review_id} not found.")
        from app.models.project import Project

        res = await db.execute(select(Project).filter(Project.id == review.project_id))
        proj = res.scalars().first()
        owner_scope = proj.owner_id if proj else 0

    metrics = await ReviewService.get_metrics(db, review_id, owner_scope)
    return ReviewMetricsResponse.model_validate(metrics)


@router.get("/{review_id}/reports", response_class=StandardJSONResponse)
async def get_review_reports(
    review_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Lists report document references generated for a specific review run."""
    owner_scope = current_user.id if not current_user.is_superuser else 0
    if current_user.is_superuser:
        from app.db.repositories.review_repository import ReviewRepository

        review_repo = ReviewRepository(db)
        review = await review_repo.get(review_id)
        if not review:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(f"Review with ID {review_id} not found.")
        from app.models.project import Project

        res = await db.execute(select(Project).filter(Project.id == review.project_id))
        proj = res.scalars().first()
        owner_scope = proj.owner_id if proj else 0

    reports = await ReviewService.get_reports(db, review_id, owner_scope)
    return [ReportResponse.model_validate(r) for r in reports]
