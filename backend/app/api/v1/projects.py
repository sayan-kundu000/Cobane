from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.core.responses import StandardJSONResponse
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectStatsResponse
from app.schemas.query import QueryParams, get_query_params, PaginatedResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_class=StandardJSONResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Creates a new code project workspace linked to the active user account."""
    project = await ProjectService.create_project(db, project_in, current_user.id)
    return ProjectResponse.model_validate(project)


@router.get("", response_class=StandardJSONResponse)
async def list_projects(
    params: QueryParams = Depends(get_query_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists projects with optional search, sorting, filtering, and pagination. Scoped by owner."""
    owner_scope = None if current_user.is_superuser else current_user.id
    projects, total = await ProjectService.list_projects(db, params, owner_id=owner_scope)

    total_pages = (total + params.pagination.page_size - 1) // params.pagination.page_size if total > 0 else 0
    items = [ProjectResponse.model_validate(p) for p in projects]

    return {
        "items": items,
        "pagination": {
            "page": params.pagination.page,
            "page_size": params.pagination.page_size,
            "total_items": total,
            "total_pages": total_pages,
        },
    }


@router.get("/{project_id}", response_class=StandardJSONResponse)
async def get_project(
    project_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieves metadata properties for a specific project workspace."""
    if current_user.is_superuser:
        from app.db.repositories.project_repository import ProjectRepository

        project_repo = ProjectRepository(db)
        project = await project_repo.get(project_id)
        if not project:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(f"Project with ID {project_id} not found.")
    else:
        project = await ProjectService.get_project(db, project_id, owner_id=current_user.id)

    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_class=StandardJSONResponse)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates name and description parameters on a project workspace."""
    owner_scope = current_user.id if not current_user.is_superuser else 0
    # Wait, if superuser, we need to bypass owner filter
    if current_user.is_superuser:
        from app.db.repositories.project_repository import ProjectRepository

        project_repo = ProjectRepository(db)
        project = await project_repo.get(project_id)
        if not project:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(f"Project with ID {project_id} not found.")
        owner_scope = project.owner_id

    updated = await ProjectService.update_project(db, project_id, project_in, owner_scope)
    return ProjectResponse.model_validate(updated)


@router.delete("/{project_id}", response_class=StandardJSONResponse)
async def delete_project(
    project_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Removes a project workspace and all its cascading metrics/reviews."""
    owner_scope = current_user.id if not current_user.is_superuser else 0
    if current_user.is_superuser:
        from app.db.repositories.project_repository import ProjectRepository

        project_repo = ProjectRepository(db)
        project = await project_repo.get(project_id)
        if not project:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(f"Project with ID {project_id} not found.")
        owner_scope = project.owner_id

    await ProjectService.delete_project(db, project_id, owner_scope)
    return {"message": "Project successfully deleted."}


@router.get("/{project_id}/stats", response_class=StandardJSONResponse)
async def get_project_stats(
    project_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieves aggregated quality dashboard stats for a project."""
    owner_scope = current_user.id if not current_user.is_superuser else 0
    if current_user.is_superuser:
        from app.db.repositories.project_repository import ProjectRepository

        project_repo = ProjectRepository(db)
        project = await project_repo.get(project_id)
        if not project:
            from app.core.exceptions import NotFoundException

            raise NotFoundException(f"Project with ID {project_id} not found.")
        owner_scope = project.owner_id

    stats = await ProjectService.get_project_stats(db, project_id, owner_scope)
    return stats


@router.post("/{project_id}/upload", response_class=StandardJSONResponse)
async def upload_project_file(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Saves a code snippet or codebase archive and registers it as an UploadedSource."""
    # Validate project and ownership
    if not current_user.is_superuser:
        await ProjectService.get_project(db, project_id, current_user.id)
    else:
        from app.db.repositories.project_repository import ProjectRepository
        project_repo = ProjectRepository(db)
        project = await project_repo.get(project_id)
        if not project:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(f"Project with ID {project_id} not found.")

    import os
    import hashlib
    from app.models.project import UploadedSource
    from app.utils.path_helpers import ensure_directory_exists

    upload_dir = "uploads/processed"
    ensure_directory_exists(upload_dir)

    # Calculate filename and save destination
    safe_filename = f"{project_id}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)

    # Read content to write to file and compute hash
    content = await file.read()
    file_size = len(content)
    sha256 = hashlib.sha256(content).hexdigest()

    # Save to disk
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Determine programming language from extension
    ext = os.path.splitext(file.filename)[1].lower()
    language = "python" if ext == ".py" else ext.strip(".") or "txt"

    # Create UploadedSource record in database
    uploaded_source = UploadedSource(
        project_id=project_id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        language=language,
        sha256_hash=sha256,
        status="processed"
    )
    db.add(uploaded_source)
    await db.commit()
    await db.refresh(uploaded_source)

    return {
        "id": uploaded_source.id,
        "project_id": uploaded_source.project_id,
        "filename": uploaded_source.filename,
        "file_size": uploaded_source.file_size,
        "language": uploaded_source.language,
        "status": uploaded_source.status
    }
