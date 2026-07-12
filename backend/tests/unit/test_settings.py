import pytest
from httpx import AsyncClient

async def get_auth_header(client: AsyncClient, username="setuser", email="setuser@cobane.ai") -> dict:
    """Helper getting valid user login bearer tokens."""
    reg_payload = {"username": username, "email": email, "password": "Password123", "password_confirm": "Password123"}
    await client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123"})
    tokens = login_res.json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}

@pytest.mark.anyio
async def test_user_preference_and_system_settings(client: AsyncClient):
    # Verify public access for system settings
    res_sys = await client.get("/api/v1/settings/system")
    assert res_sys.status_code == 200
    sys_data = res_sys.json()["data"]
    assert sys_data["app_name"] == "Cobane Code Review Assistant"
    assert sys_data["features"]["ai_review"] is True

    # User settings (requires auth)
    auth_header = await get_auth_header(client)
    res_get = await client.get("/api/v1/settings/user", headers=auth_header)
    assert res_get.status_code == 200
    user_prefs = res_get.json()["data"]
    assert user_prefs["theme"] == "light"
    assert user_prefs["receiving_notifications"] is True

    # Modify settings theme
    res_update = await client.put(
        "/api/v1/settings/user",
        json={"theme": "dark", "receiving_notifications": False},
        headers=auth_header
    )
    assert res_update.status_code == 200
    updated_prefs = res_update.json()["data"]
    assert updated_prefs["theme"] == "dark"
    assert updated_prefs["receiving_notifications"] is False

    # Validation constraints check (invalid theme)
    res_invalid = await client.put(
        "/api/v1/settings/user",
        json={"theme": "blue"},
        headers=auth_header
    )
    assert res_invalid.status_code == 422
    assert res_invalid.json()["error"] == "VALIDATION_ERROR"
