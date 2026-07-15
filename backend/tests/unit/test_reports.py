import pytest
from httpx import AsyncClient
from tests.conftest import TestingSessionLocal
from app.models.project import Project, UploadedSource
from app.models.review import Review, Report


async def seed_report(client: AsyncClient, username="repuser", email="repuser@cobane.ai") -> tuple[dict, int]:
    """Registers user, project, review and seeds a Report record."""
    # Register/Login
    reg_payload = {"username": username, "email": email, "password": "Password123", "password_confirm": "Password123"}
    await client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123"})
    tokens = login_res.json()["data"]
    auth_header = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Create Project & UploadedSource & Review & Report
    async with TestingSessionLocal() as session:
        proj = Project(name="Report Project", owner_id=1)  # owner_id = 1 assuming first registered user is ID 1
        session.add(proj)
        await session.flush()

        source = UploadedSource(
            project_id=proj.id,
            filename="rep.py",
            file_path="uploads/rep.py",
            file_size=10,
            language="python",
            sha256_hash="hash",
            status="processed",
        )
        session.add(source)
        await session.flush()

        review = Review(
            project_id=proj.id,
            uploaded_source_id=source.id,
            status="completed",
            pylint_score=9.0,
            radon_mi_score=95.0,
            bandit_issues_count=0,
            ai_review_completed=True,
        )
        session.add(review)
        await session.flush()

        report = Report(review_id=review.id, format="pdf", file_path="reports/exports/test-report.pdf")
        session.add(report)
        await session.commit()
        report_id = report.id

    return auth_header, report_id


@pytest.mark.anyio
async def test_reports_routing_endpoints(client: AsyncClient):
    auth_header, report_id = await seed_report(client)

    # 1. List all reports
    res_list = await client.get("/api/v1/reports", headers=auth_header)
    assert res_list.status_code == 200
    reports = res_list.json()["data"]
    assert len(reports) == 1
    assert reports[0]["id"] == report_id
    assert reports[0]["format"] == "pdf"

    # 2. Get single report details
    res_get = await client.get(f"/api/v1/reports/{report_id}", headers=auth_header)
    assert res_get.status_code == 200
    data = res_get.json()["data"]
    assert data["format"] == "pdf"
    assert "file_path" in data

    # 3. Get download references stub
    res_dl = await client.get(f"/api/v1/reports/{report_id}/download", headers=auth_header)
    assert res_dl.status_code == 200
    dl_data = res_dl.json()["data"]
    assert "download_url" in dl_data
    assert dl_data["format"] == "pdf"

    # 4. Check Not Found
    res_not_found = await client.get("/api/v1/reports/999", headers=auth_header)
    assert res_not_found.status_code == 404
