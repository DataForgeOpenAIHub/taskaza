import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def token_and_headers(async_client):
    await async_client.post("/signup", json={"username": "keyuser", "password": "pass"})
    token_res = await async_client.post(
        "/token", data={"username": "keyuser", "password": "pass"}
    )
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return token, headers


@pytest.mark.asyncio
async def test_api_key_lifecycle(async_client, token_and_headers):
    token, headers = token_and_headers

    create_res = await async_client.post("/apikeys", headers=headers)
    assert create_res.status_code == 201
    data = create_res.json()
    key = data["key"]
    api_key_id = data["id"]

    list_res = await async_client.get("/apikeys", headers=headers)
    assert list_res.status_code == 200
    listed = list_res.json()[0]
    assert listed["id"] == api_key_id
    assert listed["prefix"] == key[:8]
    assert listed["revoked"] is False

    # revoke
    del_res = await async_client.delete(f"/apikeys/{api_key_id}", headers=headers)
    assert del_res.status_code == 204

    list_res = await async_client.get("/apikeys", headers=headers)
    assert list_res.json()[0]["revoked"] is True

    # attempt to use revoked key
    headers_with_key = {**headers, "X-API-Key": key}
    res = await async_client.get("/tasks/", headers=headers_with_key)
    assert res.status_code == 403
