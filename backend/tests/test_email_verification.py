import os

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def auth_headers(async_client):
    API_KEY = os.getenv("TSKZ_HTTP_API_KEY", "123456")
    username = "verifyuser"
    password = "secret"
    await async_client.post(
        "/signup",
        json={
            "username": username,
            "password": password,
            "email": "verify@example.com",
        },
    )
    token_res = await async_client.post(
        "/token", data={"username": username, "password": password}
    )
    token = token_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "X-API-Key": API_KEY}


@pytest.mark.asyncio
async def test_email_verification_flow(async_client, auth_headers):
    # Initially unverified
    res = await async_client.get("/users/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email_verified"] is False

    # Request verification token
    res = await async_client.post("/auth/request-verification", headers=auth_headers)
    assert res.status_code == 200
    token = res.json()["detail"]

    # Verify using token
    res = await async_client.post("/auth/verify", json={"token": token})
    assert res.status_code == 200

    # Email should now be verified
    res = await async_client.get("/users/me", headers=auth_headers)
    assert res.json()["email_verified"] is True
