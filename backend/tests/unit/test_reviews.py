import pytest
from httpx import AsyncClient
from tests.conftest import TestingSessionLocal
from app.models.project import Project, UploadedSource
from app.models.review import Review


async def get_auth_header_and_project(
    client: AsyncClient, username="revuser", email="revuser@cobane.ai"
) -> tuple[dict, int]:
    """Helper registering user, creating a project, and seeding an uploaded source."""
    reg_payload = {"username": username, "email": email, "password": "Password123", "password_confirm": "Password123"}
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {"email": email, "password": "Password123"}
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    tokens = login_res.json()["data"]
    auth_header = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Create project
    proj_res = await client.post("/api/v1/projects", json={"name": "Review Target Proj"}, headers=auth_header)
    project_id = proj_res.json()["data"]["id"]

    # Seed UploadedSource directly to SQLite test DB
    async with TestingSessionLocal() as session:
        uploaded_source = UploadedSource(
            project_id=project_id,
            filename="source_code.py",
            file_path="uploads/source_code.py",
            file_size=1024,
            language="python",
            sha256_hash="f6a9e14498fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            status="processed",
        )
        session.add(uploaded_source)
        await session.commit()

    return auth_header, project_id


@pytest.mark.anyio
async def test_trigger_and_get_review_workflows(client: AsyncClient):
    auth_header, project_id = await get_auth_header_and_project(client)

    # 1. Trigger code review
    trigger_payload = {"project_id": project_id}
    res = await client.post("/api/v1/reviews", json=trigger_payload, headers=auth_header)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    review_id = data["data"]["id"]
    assert data["data"]["status"] == "completed"
    assert data["data"]["ai_review_completed"] is True
    assert data["data"]["pylint_score"] == 10.0

    # 2. Get review metadata details
    res_get = await client.get(f"/api/v1/reviews/{review_id}", headers=auth_header)
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert data_get["success"] is True
    assert data_get["data"]["status"] == "completed"

    # 3. Retrieve nested review findings
    res_findings = await client.get(f"/api/v1/reviews/{review_id}/findings", headers=auth_header)
    assert res_findings.status_code == 200
    findings = res_findings.json()["data"]
    assert len(findings) >= 2  # contains pylint and bandit stubs
    assert findings[0]["provider"] in {"pylint", "bandit", "ai"}

    # 4. Retrieve nested review metrics
    res_metrics = await client.get(f"/api/v1/reviews/{review_id}/metrics", headers=auth_header)
    assert res_metrics.status_code == 200
    metrics = res_metrics.json()["data"]
    assert metrics["cyclomatic_complexity"] == 3
    assert metrics["maintainability_index"] == 90.0

    # 5. Retrieve nested review reports
    res_reports = await client.get(f"/api/v1/reviews/{review_id}/reports", headers=auth_header)
    assert res_reports.status_code == 200
    reports = res_reports.json()["data"]
    assert len(reports) == 1
    assert reports[0]["format"] == "pdf"


@pytest.mark.anyio
async def test_list_and_delete_reviews(client: AsyncClient):
    auth_header, project_id = await get_auth_header_and_project(client, "listrev", "listrev@cobane.ai")

    # Trigger review
    res_trigger = await client.post("/api/v1/reviews", json={"project_id": project_id}, headers=auth_header)
    review_id = res_trigger.json()["data"]["id"]

    # List reviews
    res_list = await client.get(f"/api/v1/reviews?project_id={project_id}", headers=auth_header)
    assert res_list.status_code == 200
    data_list = res_list.json()
    assert len(data_list["data"]["items"]) == 1
    assert data_list["data"]["items"][0]["id"] == review_id

    # Filter checks (pylint score, status, language)
    res_filter1 = await client.get(f"/api/v1/reviews?min_score=9.0", headers=auth_header)
    assert len(res_filter1.json()["data"]["items"]) == 1

    res_filter2 = await client.get(f"/api/v1/reviews?max_score=5.0", headers=auth_header)
    assert len(res_filter2.json()["data"]["items"]) == 0

    # Sorting whitelists validation
    res_sort = await client.get(f"/api/v1/reviews?sort_by=pylint_score&ascending=false", headers=auth_header)
    assert res_sort.status_code == 200

    res_invalid_sort = await client.get(f"/api/v1/reviews?sort_by=non_existent_column", headers=auth_header)
    assert res_invalid_sort.status_code == 422

    # Delete review
    res_del = await client.delete(f"/api/v1/reviews/{review_id}", headers=auth_header)
    assert res_del.status_code == 200
    assert res_del.json()["data"]["message"] == "Review successfully deleted."

    # Verify deleted status
    res_get = await client.get(f"/api/v1/reviews/{review_id}", headers=auth_header)
    assert res_get.status_code == 404
