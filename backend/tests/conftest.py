"""
Shared fixtures for all tests.
Uses an in-memory SQLite database so tests never touch the real DB.
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# ── CRITICAL: import ALL models so they register with Base.metadata ──
import api.models  # noqa: F401  (this runs the __init__.py which imports every model)
from core.database import Base, get_db

# ── Shared in-memory SQLite for the entire test session ──
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionFactory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    """DB dependency override — uses in-memory test DB."""
    async with TestSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables ONCE for the whole test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture()
async def client(create_tables):  # depend on create_tables so tables exist first
    """Return an async test client with the test DB wired in."""
    os.makedirs("./uploads", exist_ok=True)

    from main import app
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def auth_headers(client: AsyncClient):
    """Register a fresh test user (or login if already exists) and return Bearer headers."""
    payload = {"name": "Test User", "email": "testuser@example.com", "password": "TestPass123!"}
    resp = await client.post("/api/auth/register", json=payload)
    if resp.status_code == 409:  # already registered
        resp = await client.post("/api/auth/login", json={
            "email": payload["email"],
            "password": payload["password"],
        })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

