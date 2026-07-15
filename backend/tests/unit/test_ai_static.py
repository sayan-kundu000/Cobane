import pytest
from httpx import AsyncClient


async def get_auth_header(client: AsyncClient, username="cfguser", email="cfguser@cobane.ai") -> dict:
    reg_payload = {"username": username, "email": email, "password": "Password123", "password_confirm": "Password123"}
    await client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123"})
    tokens = login_res.json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.mark.anyio
async def test_ai_and_static_analysis_config_endpoints(client: AsyncClient):
    auth_header = await get_auth_header(client)

    # 1. AI integration config
    res_ai_cfg = await client.get("/api/v1/ai/config", headers=auth_header)
    assert res_ai_cfg.status_code == 200
    ai_cfg = res_ai_cfg.json()["data"]
    assert "provider" in ai_cfg
    assert "model_engine" in ai_cfg

    # 2. AI review prompt templates
    res_prompts = await client.get("/api/v1/ai/prompts", headers=auth_header)
    assert res_prompts.status_code == 200
    prompts = res_prompts.json()["data"]
    assert "templates" in prompts
    assert len(prompts["templates"]) >= 2

    # 3. Static check tools config
    res_sa_cfg = await client.get("/api/v1/static-analysis/config", headers=auth_header)
    assert res_sa_cfg.status_code == 200
    sa_cfg = res_sa_cfg.json()["data"]
    assert "checkers" in sa_cfg
    assert sa_cfg["checkers"]["pylint"]["enabled"] is True
