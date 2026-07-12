from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from app.db.repositories.base_repository import BaseRepository
from app.models.review import Review
from app.schemas.query import QueryParams
from app.core.exceptions import ValidationException


class ReviewRepository(BaseRepository[Review]):
    """Repository managing Review metrics and reports query aggregations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Review, db_session)

    async def get_project_stats(self, project_id_val: int) -> Dict[str, Any]:
        """Calculates project dashboard aggregates (average scores, issues count) for a project."""
        query = select(
            func.avg(Review.pylint_score).label("avg_pylint"),
            func.avg(Review.radon_mi_score).label("avg_radon"),
            func.sum(Review.bandit_issues_count).label("total_bandit_issues"),
            func.count(Review.id).label("total_reviews"),
        ).filter(Review.project_id == project_id_val)

        result = await self.db.execute(query)
        stats = result.first()

        if stats and stats.total_reviews > 0:
            return {
                "average_pylint_score": float(stats.avg_pylint or 0.0),
                "average_maintainability_index": float(stats.avg_radon or 0.0),
                "total_bandit_vulnerabilities": int(stats.total_bandit_issues or 0),
                "total_reviews_conducted": int(stats.total_reviews),
            }
        return {
            "average_pylint_score": 0.0,
            "average_maintainability_index": 0.0,
            "total_bandit_vulnerabilities": 0,
            "total_reviews_conducted": 0,
        }

    async def search_and_filter(
        self, params: QueryParams, project_id: Optional[int] = None
    ) -> Tuple[List[Review], int]:
        """Lists reviews matching paginated, searched, sorted, and filtered criteria."""
        query = select(Review)

        # Enforce project scope
        if project_id is not None:
            query = query.filter(Review.project_id == project_id)
        elif params.filters.project_id is not None:
            query = query.filter(Review.project_id == params.filters.project_id)

        # Join setup to avoid duplicate joins
        joined_source = False

        # Keyword search (status or source filename)
        if params.search.q:
            from app.models.project import UploadedSource

            keyword = f"%{params.search.q}%"
            query = query.join(UploadedSource)
            joined_source = True
            query = query.filter(Review.status.ilike(keyword) | UploadedSource.filename.ilike(keyword))

        # Apply specific filters
        if params.filters.status:
            query = query.filter(Review.status == params.filters.status)

        if params.filters.language:
            from app.models.project import UploadedSource

            if not joined_source:
                query = query.join(UploadedSource)
                joined_source = True
            query = query.filter(UploadedSource.language.ilike(params.filters.language))

        if params.filters.min_score is not None:
            query = query.filter(Review.pylint_score >= params.filters.min_score)

        if params.filters.max_score is not None:
            query = query.filter(Review.pylint_score <= params.filters.max_score)

        if params.filters.start_date:
            query = query.filter(Review.created_at >= params.filters.start_date)

        if params.filters.end_date:
            query = query.filter(Review.created_at <= params.filters.end_date)

        # Calculate matching total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_items = count_result.scalar_one()

        # Validate sorting fields
        sort_field = params.sort.sort_by
        allowed_sort_fields = {"id", "status", "pylint_score", "radon_mi_score", "bandit_issues_count", "created_at"}
        if sort_field not in allowed_sort_fields:
            raise ValidationException(f"Sorting by field '{sort_field}' is not supported for reviews.")

        sort_attr = getattr(Review, sort_field)
        query = query.order_by(sort_attr if params.sort.ascending else desc(sort_attr))

        # Paginate results
        query = query.offset(params.pagination.skip).limit(params.pagination.limit)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total_items
