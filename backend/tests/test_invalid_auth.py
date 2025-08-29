import pytest
import pytest_asyncio

INVALID_API_KEY = "invalid-key"
BAD_TOKEN = "Bearer badtoken.fake.jwt"

TASK_ENDPOINTS = [
    ("get", "/tasks/"),
    ("post", "/tasks/"),
    ("get", "/tasks/999"),
    ("patch", "/tasks/999"),
    ("put", "/tasks/999"),
    ("delete", "/tasks/999"),
]


def requires_body(method: str) -> bool:
    return method in {"post", "put", "patch"}


@pytest_asyncio.fixture
async def valid_api_key(async_client):
    await async_client.post("/signup", json={"username": "apiuser", "password": "pass"})
    token_res = await async_client.post(
        "/token", data={"username": "apiuser", "password": "pass"}
    )
    token = token_res.json()["access_token"]
    key_res = await async_client.post(
        "/apikeys", headers={"Authorization": f"Bearer {token}"}
    )
    return key_res.json()["key"]


@pytest.mark.parametrize("method,endpoint", TASK_ENDPOINTS)
@pytest.mark.asyncio
async def test_missing_jwt_token(async_client, valid_api_key, method, endpoint):
    headers = {"X-API-Key": valid_api_key}
    kwargs = {"headers": headers}
    if requires_body(method):
        kwargs["json"] = {}
    response = await getattr(async_client, method)(endpoint, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize("method,endpoint", TASK_ENDPOINTS)
@pytest.mark.asyncio
async def test_missing_api_key(async_client, auth_headers_only_token, method, endpoint):
    headers = auth_headers_only_token.copy()
    headers.pop("X-API-Key", None)
    kwargs = {"headers": headers}
    if requires_body(method):
        kwargs["json"] = {}
    response = await getattr(async_client, method)(endpoint, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize("method,endpoint", TASK_ENDPOINTS)
@pytest.mark.asyncio
async def test_invalid_jwt_token(async_client, valid_api_key, method, endpoint):
    headers = {"Authorization": BAD_TOKEN, "X-API-Key": valid_api_key}
    kwargs = {"headers": headers}
    if requires_body(method):
        kwargs["json"] = {}
    response = await getattr(async_client, method)(endpoint, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize("method,endpoint", TASK_ENDPOINTS)
@pytest.mark.asyncio
async def test_invalid_api_key(async_client, auth_headers_only_token, method, endpoint):
    headers = auth_headers_only_token.copy()
    headers["X-API-Key"] = INVALID_API_KEY
    kwargs = {"headers": headers}
    if requires_body(method):
        kwargs["json"] = {}
    response = await getattr(async_client, method)(endpoint, **kwargs)
    assert response.status_code == 403
