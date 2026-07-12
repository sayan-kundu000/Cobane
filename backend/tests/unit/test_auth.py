import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_auth_and_profile_workflows(client: AsyncClient):
    # 1. Register a new user account
    reg_payload = {
        "username": "testuser",
        "email": "testuser@cobane.ai",
        "password": "Password123",
        "password_confirm": "Password123"
    }
    
    reg_response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["success"] is True
    assert reg_data["data"]["username"] == "testuser"
    assert reg_data["data"]["email"] == "testuser@cobane.ai"

    # 2. Attempt duplicate registration checks
    dup_response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_response.status_code == 422
    dup_data = dup_response.json()
    assert dup_data["success"] is False
    assert dup_data["error"] == "VALIDATION_ERROR"

    # 3. Successful login retrieving access and refresh tokens
    login_payload = {
        "email": "testuser@cobane.ai",
        "password": "Password123"
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["success"] is True
    tokens = login_data["data"]
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    access_token = tokens["access_token"]
    auth_header = {"Authorization": f"Bearer {access_token}"}

    # 4. Get Current User info (Protected Route)
    me_response = await client.get("/api/v1/users/me", headers=auth_header)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["success"] is True
    assert me_data["data"]["username"] == "testuser"

    # 5. Access without headers must fail
    fail_response = await client.get("/api/v1/users/me")
    assert fail_response.status_code == 401
    
    # 6. Update Profile biography details (Protected Route)
    profile_payload = {
        "full_name": "Test User Account",
        "bio": "Software developer testing AI Code Review systems."
    }
    prof_response = await client.put("/api/v1/users/me/profile", json=profile_payload, headers=auth_header)
    assert prof_response.status_code == 200
    prof_data = prof_response.json()
    assert prof_data["success"] is True
    assert prof_data["data"]["full_name"] == "Test User Account"
    assert prof_data["data"]["bio"] == "Software developer testing AI Code Review systems."
