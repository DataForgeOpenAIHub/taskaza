import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def auth_headers(async_client):
    username = "user1"
    password = "secret"
    await async_client.post(
        "/signup", json={"username": username, "password": password}
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
async def test_get_and_update_user(async_client, auth_headers):
    res = await async_client.get("/users/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["username"] == "user1"

    update = {"email": "user1@example.com", "display_name": "User One"}
    res = await async_client.put("/users/me", json=update, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "user1@example.com"
    assert data["display_name"] == "User One"

    patch_data = {"display_name": "User 1"}
    res = await async_client.patch("/users/me", json=patch_data, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["display_name"] == "User 1"
