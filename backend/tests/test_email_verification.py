import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def auth_headers(async_client):
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

    key_res = await async_client.post(
        "/apikeys", headers={"Authorization": f"Bearer {token}"}
    )
    api_key = key_res.json()["key"]

    return {"Authorization": f"Bearer {token}", "X-API-Key": api_key}


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
