import pytest
from httpx import AsyncClient
from tests.conftest import TestingSessionLocal
from app.models.project import Project, UploadedSource


async def get_auth_header(client: AsyncClient, username="projuser", email="projuser@cobane.ai") -> dict:
    """Helper to register and log in a user, returning the authorization header."""
    reg_payload = {"username": username, "email": email, "password": "Password123", "password_confirm": "Password123"}
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {"email": email, "password": "Password123"}
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    tokens = login_res.json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.mark.anyio
async def test_create_and_get_project(client: AsyncClient):
    auth_header = await get_auth_header(client)

    # 1. Create project
    create_payload = {"name": "Test Python Workspace", "description": "A repository of Python files."}
    res = await client.post("/api/v1/projects", json=create_payload, headers=auth_header)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    project_id = data["data"]["id"]
    assert data["data"]["name"] == "Test Python Workspace"
    assert data["data"]["description"] == "A repository of Python files."

    # 2. Retrieve project details
    res_get = await client.get(f"/api/v1/projects/{project_id}", headers=auth_header)
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert data_get["success"] is True
    assert data_get["data"]["id"] == project_id


@pytest.mark.anyio
async def test_list_projects_filtering_sorting_search(client: AsyncClient):
    auth_header = await get_auth_header(client, "listuser", "listuser@cobane.ai")

    # Create two projects
    await client.post(
        "/api/v1/projects", json={"name": "alpha-project", "description": "Desc alpha"}, headers=auth_header
    )
    await client.post(
        "/api/v1/projects", json={"name": "beta-project", "description": "Desc beta"}, headers=auth_header
    )

    # Search keyword
    res_search = await client.get("/api/v1/projects?q=alpha", headers=auth_header)
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert len(data_search["data"]["items"]) == 1
    assert data_search["data"]["items"][0]["name"] == "alpha-project"

    # Sorting
    res_sort = await client.get("/api/v1/projects?sort_by=name&ascending=false", headers=auth_header)
    data_sort = res_sort.json()
    assert len(data_sort["data"]["items"]) == 2
    assert data_sort["data"]["items"][0]["name"] == "beta-project"
    assert data_sort["data"]["items"][1]["name"] == "alpha-project"

    # Invalid sort field validation
    res_invalid_sort = await client.get("/api/v1/projects?sort_by=invalid_field", headers=auth_header)
    assert res_invalid_sort.status_code == 422
    assert res_invalid_sort.json()["error"] == "VALIDATION_ERROR"

    # Pagination metadata
    res_page = await client.get("/api/v1/projects?page=1&page_size=1", headers=auth_header)
    data_page = res_page.json()
    assert len(data_page["data"]["items"]) == 1
    assert data_page["data"]["pagination"]["total_items"] == 2
    assert data_page["data"]["pagination"]["total_pages"] == 2


@pytest.mark.anyio
async def test_update_and_delete_project(client: AsyncClient):
    auth_header = await get_auth_header(client, "edituser", "edituser@cobane.ai")

    # Create project
    res_create = await client.post("/api/v1/projects", json={"name": "old-name"}, headers=auth_header)
    project_id = res_create.json()["data"]["id"]

    # Update project
    res_update = await client.put(
        f"/api/v1/projects/{project_id}", json={"name": "new-name", "description": "updated desc"}, headers=auth_header
    )
    assert res_update.status_code == 200
    assert res_update.json()["data"]["name"] == "new-name"
    assert res_update.json()["data"]["description"] == "updated desc"

    # Delete project
    res_delete = await client.delete(f"/api/v1/projects/{project_id}", headers=auth_header)
    assert res_delete.status_code == 200
    assert res_delete.json()["data"]["message"] == "Project successfully deleted."

    # Verify not found
    res_get = await client.get(f"/api/v1/projects/{project_id}", headers=auth_header)
    assert res_get.status_code == 404


@pytest.mark.anyio
async def test_project_stats_and_language_filter(client: AsyncClient):
    auth_header = await get_auth_header(client, "statsuser", "statsuser@cobane.ai")

    # Create project
    res_create = await client.post("/api/v1/projects", json={"name": "stats-proj"}, headers=auth_header)
    project_id = res_create.json()["data"]["id"]

    # Retrieve stats (should be empty defaults since no reviews exist)
    res_stats = await client.get(f"/api/v1/projects/{project_id}/stats", headers=auth_header)
    assert res_stats.status_code == 200
    stats = res_stats.json()["data"]
    assert stats["total_reviews_conducted"] == 0
    assert stats["average_pylint_score"] == 0.0

    # Seed an uploaded source directly to SQLite db to test filtering by language
    async with TestingSessionLocal() as session:
        uploaded_source = UploadedSource(
            project_id=project_id,
            filename="main.py",
            file_path="uploads/main.py",
            file_size=500,
            language="python",
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            status="processed",
        )
        session.add(uploaded_source)
        await session.commit()

    # Filter projects by language = python
    res_lang = await client.get("/api/v1/projects?language=python", headers=auth_header)
    assert res_lang.status_code == 200
    items = res_lang.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["id"] == project_id

    # Filter by non-existent language
    res_no_lang = await client.get("/api/v1/projects?language=rust", headers=auth_header)
    assert res_no_lang.status_code == 200
    assert len(res_no_lang.json()["data"]["items"]) == 0
