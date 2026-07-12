from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.core.responses import StandardJSONResponse
from app.models.user import User
from app.models.review import Report, Review
from app.models.project import Project
from app.schemas.review import ReportResponse
from app.core.exceptions import NotFoundException, ForbiddenException

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_class=StandardJSONResponse)
async def list_all_reports(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Lists all generated PDF/HTML/Markdown report export references accessible to the user."""
    if current_user.is_superuser:
        result = await db.execute(select(Report))
        reports = result.scalars().all()
    else:
        # Join projects to filter by project owner
        result = await db.execute(select(Report).join(Review).join(Project).filter(Project.owner_id == current_user.id))
        reports = result.scalars().all()

    return [ReportResponse.model_validate(r) for r in reports]


@router.get("/{report_id}", response_class=StandardJSONResponse)
async def get_report_details(
    report_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieves metadata properties for a specific report export record."""
    result = await db.execute(select(Report).filter(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise NotFoundException(f"Report export with ID {report_id} not found.")

    # Access scoping validation
    if not current_user.is_superuser:
        # Check review owner
        res_review = await db.execute(select(Review).filter(Review.id == report.review_id))
        review = res_review.scalars().first()
        if review:
            res_project = await db.execute(select(Project).filter(Project.id == review.project_id))
            project = res_project.scalars().first()
            if not project or project.owner_id != current_user.id:
                raise ForbiddenException("Access to this report is restricted.")

    return ReportResponse.model_validate(report)


@router.get("/{report_id}/download", response_class=StandardJSONResponse)
async def download_report_file(
    report_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Downloads the physical report document. Stub returns metadata download endpoint references."""
    # Run the same auth validation check:
    await get_report_details(report_id, current_user, db)

    return {
        "message": "Report download initiated successfully.",
        "download_url": f"/api/v1/reports/{report_id}/download/stream",
        "format": "pdf",
    }
