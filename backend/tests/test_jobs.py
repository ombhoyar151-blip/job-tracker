"""
Tests for: /api/jobs — list, seed, get by id, save/unsave
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _seed(client: AsyncClient, auth_headers):
    """Helper: seed jobs and return first job id."""
    await client.post("/api/jobs/seed", headers=auth_headers)
    resp = await client.get("/api/jobs", headers=auth_headers)
    jobs = resp.json()["jobs"]
    return jobs[0]["id"] if jobs else None


# ─────────────────────────────────────────────
#  1. Seed endpoint
# ─────────────────────────────────────────────
async def test_seed_jobs(client: AsyncClient, auth_headers):
    resp = await client.post("/api/jobs/seed", headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert "message" in body


async def test_seed_jobs_idempotent(client: AsyncClient, auth_headers):
    """Second seed should skip and return existing count."""
    await client.post("/api/jobs/seed", headers=auth_headers)
    resp = await client.post("/api/jobs/seed", headers=auth_headers)
    assert resp.status_code == 201
    assert "already has" in resp.json()["message"] or "Seeded" in resp.json()["message"]


# ─────────────────────────────────────────────
#  2. List jobs
# ─────────────────────────────────────────────
async def test_list_jobs_requires_auth(client: AsyncClient):
    resp = await client.get("/api/jobs")
    assert resp.status_code == 403


async def test_list_jobs(client: AsyncClient, auth_headers):
    await client.post("/api/jobs/seed", headers=auth_headers)
    resp = await client.get("/api/jobs", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "jobs" in body
    assert "total" in body
    assert "page" in body
    assert isinstance(body["jobs"], list)


async def test_list_jobs_pagination(client: AsyncClient, auth_headers):
    await client.post("/api/jobs/seed", headers=auth_headers)
    resp = await client.get("/api/jobs?page=1&page_size=5", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["jobs"]) <= 5
    assert body["page"] == 1
    assert body["page_size"] == 5


async def test_list_jobs_search(client: AsyncClient, auth_headers):
    await client.post("/api/jobs/seed", headers=auth_headers)
    resp = await client.get("/api/jobs?q=engineer", headers=auth_headers)
    assert resp.status_code == 200


# ─────────────────────────────────────────────
#  3. Get single job
# ─────────────────────────────────────────────
async def test_get_job_by_id(client: AsyncClient, auth_headers):
    job_id = await _seed(client, auth_headers)
    if not job_id:
        pytest.skip("No jobs seeded")
    resp = await client.get(f"/api/jobs/{job_id}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == job_id
    assert "title" in body
    assert "company" in body


async def test_get_nonexistent_job(client: AsyncClient, auth_headers):
    resp = await client.get("/api/jobs/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404


# ─────────────────────────────────────────────
#  4. Save / unsave jobs
# ─────────────────────────────────────────────
async def test_save_job(client: AsyncClient, auth_headers):
    job_id = await _seed(client, auth_headers)
    if not job_id:
        pytest.skip("No jobs seeded")
    resp = await client.post(f"/api/jobs/{job_id}/save", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["saved"] is True


async def test_save_job_idempotent(client: AsyncClient, auth_headers):
    job_id = await _seed(client, auth_headers)
    if not job_id:
        pytest.skip("No jobs seeded")
    await client.post(f"/api/jobs/{job_id}/save", headers=auth_headers)
    resp = await client.post(f"/api/jobs/{job_id}/save", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["saved"] is True


async def test_unsave_job(client: AsyncClient, auth_headers):
    job_id = await _seed(client, auth_headers)
    if not job_id:
        pytest.skip("No jobs seeded")
    await client.post(f"/api/jobs/{job_id}/save", headers=auth_headers)
    resp = await client.post(f"/api/jobs/{job_id}/unsave", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["saved"] is False
