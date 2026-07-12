from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from app.db.repositories.base_repository import BaseRepository
from app.models.project import Project
from app.schemas.query import QueryParams
from app.core.exceptions import ValidationException

class ProjectRepository(BaseRepository[Project]):
    """Repository managing Project workspace mappings."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(Project, db_session)

    async def list_by_owner(self, owner_id_val: int, skip: int = 0, limit: int = 20) -> List[Project]:
        """Lists projects owned by a specific user account."""
        result = await self.db.execute(
            select(Project)
            .filter(Project.owner_id == owner_id_val)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_and_filter(
        self,
        params: QueryParams,
        owner_id: Optional[int] = None
    ) -> Tuple[List[Project], int]:
        """Lists projects matching paginated, searched, sorted, and filtered criteria."""
        query = select(Project)

        # Enforce or filter by owner_id scope
        if owner_id is not None:
            query = query.filter(Project.owner_id == owner_id)
        elif params.filters.owner_id is not None:
            query = query.filter(Project.owner_id == params.filters.owner_id)

        # Keyword search across name and description fields
        if params.search.q:
            keyword = f"%{params.search.q}%"
            query = query.filter(
                Project.name.ilike(keyword) | Project.description.ilike(keyword)
            )

        # Specific field filters
        if params.filters.language:
            # Join with UploadedSource to filter by language
            from app.models.project import UploadedSource
            query = query.join(UploadedSource).filter(
                UploadedSource.language.ilike(params.filters.language)
            ).distinct()

        # Calculate matching total count before offset bounds
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_items = count_result.scalar_one()

        # Validate sorting parameters to prevent SQL injection or arbitrary ordering
        sort_field = params.sort.sort_by
        allowed_sort_fields = {"id", "name", "created_at", "updated_at"}
        if sort_field not in allowed_sort_fields:
            raise ValidationException(f"Sorting by field '{sort_field}' is not supported for projects.")

        sort_attr = getattr(Project, sort_field)
        query = query.order_by(sort_attr if params.sort.ascending else desc(sort_attr))

        # Paginate results
        query = query.offset(params.pagination.skip).limit(params.pagination.limit)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total_items
