from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.review_repository import ReviewRepository
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectStatsResponse
from app.schemas.query import QueryParams
from app.core.exceptions import NotFoundException, ForbiddenException
from app.core.logging import app_logger


class ProjectService:
    """Service layer orchestrating project metadata management and dashboard statistics."""

    @staticmethod
    async def create_project(db: AsyncSession, project_in: ProjectCreate, owner_id: int) -> Project:
        """Saves a new project associated with the designated owner account."""
        project_repo = ProjectRepository(db)
        project_data = project_in.model_dump()
        project_data["owner_id"] = owner_id

        project = await project_repo.create(project_data)
        await db.commit()
        await db.refresh(project)

        app_logger.info("Project '%s' (ID: %d) successfully created by owner %d.", project.name, project.id, owner_id)
        return project

    @staticmethod
    async def get_project(db: AsyncSession, project_id: int, owner_id: int) -> Project:
        """Retrieves a single project after validating ownership privileges."""
        project_repo = ProjectRepository(db)
        project = await project_repo.get(project_id)

        if not project:
            raise NotFoundException(f"Project with ID {project_id} not found.")
        if project.owner_id != owner_id:
            raise ForbiddenException("Access to this project is restricted.")

        return project

    @staticmethod
    async def list_projects(
        db: AsyncSession, params: QueryParams, owner_id: Optional[int] = None
    ) -> Tuple[List[Project], int]:
        """Lists projects matching criteria, optionally scoped to a single owner."""
        project_repo = ProjectRepository(db)
        return await project_repo.search_and_filter(params, owner_id=owner_id)

    @staticmethod
    async def update_project(db: AsyncSession, project_id: int, project_in: ProjectUpdate, owner_id: int) -> Project:
        """Updates attributes of an existing project after validating ownership."""
        project_service = ProjectService()
        project = await project_service.get_project(db, project_id, owner_id)

        project_repo = ProjectRepository(db)
        update_data = {k: v for k, v in project_in.model_dump().items() if v is not None}

        updated = await project_repo.update(project, update_data)
        await db.commit()
        await db.refresh(updated)

        app_logger.info("Project ID %d successfully updated by owner %d.", project_id, owner_id)
        return updated

    @staticmethod
    async def delete_project(db: AsyncSession, project_id: int, owner_id: int) -> bool:
        """Deletes a project by ID after validating ownership."""
        project_service = ProjectService()
        # Verify ownership by trying to get the project first
        await project_service.get_project(db, project_id, owner_id)

        project_repo = ProjectRepository(db)
        success = await project_repo.delete(project_id)
        await db.commit()

        app_logger.info("Project ID %d successfully deleted by owner %d.", project_id, owner_id)
        return success

    @staticmethod
    async def get_project_stats(db: AsyncSession, project_id: int, owner_id: int) -> ProjectStatsResponse:
        """Computes summary quality analytics and issue counts across project reviews."""
        project_service = ProjectService()
        await project_service.get_project(db, project_id, owner_id)

        review_repo = ReviewRepository(db)
        stats = await review_repo.get_project_stats(project_id)

        return ProjectStatsResponse.model_validate(stats)
