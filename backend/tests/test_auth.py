"""
Tests for: /api/auth/register, /api/auth/login, /api/auth/refresh, /api/auth/me
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ─────────────────────────────────────────────
#  1. Health check
# ─────────────────────────────────────────────
async def test_health_check(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


# ─────────────────────────────────────────────
#  2. Register
# ─────────────────────────────────────────────
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "Secret123!"
    })
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_register_duplicate_email(client: AsyncClient):
    payload = {"name": "Bob", "email": "bob@example.com", "password": "Secret123!"}
    await client.post("/api/auth/register", json=payload)
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409
    assert "already registered" in resp.json()["detail"].lower()


async def test_register_invalid_email(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "name": "Charlie",
        "email": "not-an-email",
        "password": "Secret123!"
    })
    assert resp.status_code == 422  # Pydantic validation error


# ─────────────────────────────────────────────
#  3. Login
# ─────────────────────────────────────────────
async def test_login_success(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "name": "Dave",
        "email": "dave@example.com",
        "password": "MyPass456!"
    })
    resp = await client.post("/api/auth/login", json={
        "email": "dave@example.com",
        "password": "MyPass456!"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "name": "Eve",
        "email": "eve@example.com",
        "password": "Correct123!"
    })
    resp = await client.post("/api/auth/login", json={
        "email": "eve@example.com",
        "password": "WrongPass!"
    })
    assert resp.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post("/api/auth/login", json={
        "email": "ghost@example.com",
        "password": "NoUser123!"
    })
    assert resp.status_code == 401


# ─────────────────────────────────────────────
#  4. Refresh token
# ─────────────────────────────────────────────
async def test_refresh_token(client: AsyncClient):
    reg = await client.post("/api/auth/register", json={
        "name": "Frank",
        "email": "frank@example.com",
        "password": "Pass789!"
    })
    refresh_token = reg.json()["refresh_token"]
    resp = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_refresh_invalid_token(client: AsyncClient):
    resp = await client.post("/api/auth/refresh", json={"refresh_token": "totally.invalid.token"})
    assert resp.status_code == 401


# ─────────────────────────────────────────────
#  5. /me endpoint
# ─────────────────────────────────────────────
async def test_get_me(client: AsyncClient, auth_headers):
    resp = await client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    assert "email" in body
    assert body["email"] == "testuser@example.com"


async def test_get_me_no_token(client: AsyncClient):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 403  # No Bearer token → 403


async def test_get_me_invalid_token(client: AsyncClient):
    resp = await client.get("/api/auth/me", headers={"Authorization": "Bearer bad.token.here"})
    assert resp.status_code == 401
