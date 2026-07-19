from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.core.dependencies import get_db, get_current_user, oauth2_scheme
from app.core.responses import StandardJSONResponse
from app.models.user import User
from app.models.review import Report, Review, ReviewFinding
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
    report_id: int,
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Downloads the physical report document. Stub returns metadata download endpoint references."""
    # Run the same auth validation check:
    await get_report_details(report_id, current_user, db)

    return {
        "message": "Report download initiated successfully.",
        "download_url": f"/api/v1/reports/{report_id}/download/stream?token={token}",
        "format": "pdf",
    }


@router.get("/{report_id}/download/stream")
async def download_report_file_stream(report_id: int, token: str, db: AsyncSession = Depends(get_db)):
    """Streams the physical report file, generating it on the fly if not present."""
    from app.core.security import decode_token
    from app.db.repositories.user_repository import UserRepository
    from app.core.exceptions import AuthException, ForbiddenException, NotFoundException
    import os
    from fastapi.responses import FileResponse

    # 1. Authenticate user from the token query param
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise AuthException("Token claims missing identifier.")
    except Exception as e:
        raise AuthException("Could not validate credentials.") from e

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(username)
    if user is None:
        raise AuthException("User associated with token does not exist.")
    if not user.is_active:
        raise AuthException("User account is inactive.")

    # 2. Retrieve report metadata
    result = await db.execute(select(Report).filter(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise NotFoundException(f"Report export with ID {report_id} not found.")

    # 3. Access scoping validation
    if not user.is_superuser:
        # Check review owner
        res_review = await db.execute(select(Review).filter(Review.id == report.review_id))
        review = res_review.scalars().first()
        if review:
            res_project = await db.execute(select(Project).filter(Project.id == review.project_id))
            project = res_project.scalars().first()
            if not project or project.owner_id != user.id:
                raise ForbiddenException("Access to this report is restricted.")

    # 4. Resolve file path
    file_path = report.file_path
    if not os.path.isabs(file_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        abs_path = os.path.normpath(os.path.join(base_dir, file_path))
    else:
        abs_path = file_path

    # 5. Generate a placeholder PDF file if not exists
    if not os.path.exists(abs_path):
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        # Load review details and findings to present inside the report PDF
        stmt_findings = select(ReviewFinding).filter(ReviewFinding.review_id == report.review_id)
        res_findings = await db.execute(stmt_findings)
        findings = res_findings.scalars().all()

        findings_text = ""
        for idx, f in enumerate(findings, 1):
            findings_text += (
                f"({idx}) Line {f.line_number}: [{f.category.upper()}] {f.message} -> Suggestion: {f.suggestion}\n"
            )

        pdf_title = f"Cobane Code Review Audit Summary - Review #{report.review_id}"
        pdf_content = (
            f"%PDF-1.4\n"
            f"1 0 obj\n"
            f"<< /Type /Catalog /Pages 2 0 R >>\n"
            f"endobj\n"
            f"2 0 obj\n"
            f"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
            f"endobj\n"
            f"3 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << >> /Contents 4 0 R >>\n"
            f"endobj\n"
            f"4 0 obj\n"
            f"<< /Length {1000 + len(pdf_title) + len(findings_text)} >>\n"
            f"stream\n"
            f"BT /F1 24 Tf 50 800 Td ({pdf_title}) Tj ET\n"
            f"BT /F1 12 Tf 50 750 Td (Generated automatically by Cobane AI Code Review Assistant) Tj ET\n"
            f"BT /F1 10 Tf 50 720 Td (Detected Findings & Recommendations:) Tj ET\n"
        )

        y_pos = 690
        for line in findings_text.split("\n"):
            if not line.strip():
                continue
            escaped_line = line.replace("(", "\\(").replace(")", "\\)")
            # PDF text wrap or truncate for display simplicity
            chunks = [escaped_line[i : i + 85] for i in range(0, len(escaped_line), 85)]
            for chunk in chunks:
                pdf_content += f"BT /F1 9 Tf 50 {y_pos} Td ({chunk}) Tj ET\n"
                y_pos -= 15
                if y_pos < 50:
                    break
            if y_pos < 50:
                break

        pdf_content += (
            f"endstream\n"
            f"endobj\n"
            f"xref\n"
            f"0 5\n"
            f"0000000000 65535 f \n"
            f"trailer\n"
            f"<< /Size 5 /Root 1 0 R >>\n"
            f"startxref\n"
            f"300\n"
            f"%%EOF"
        )

        pdf_bytes = pdf_content.encode("utf-8")
        with open(abs_path, "wb") as f:
            f.write(pdf_bytes)

    return FileResponse(path=abs_path, media_type="application/pdf", filename=os.path.basename(abs_path))
