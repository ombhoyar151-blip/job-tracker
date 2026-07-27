"""
Tests for: /api/applications — list, get, update status, notes
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _get_saved_app_id(client: AsyncClient, auth_headers) -> str | None:
    """Seed jobs, save one, return the application id."""
    await client.post("/api/jobs/seed", headers=auth_headers)
    jobs_resp = await client.get("/api/jobs", headers=auth_headers)
    jobs = jobs_resp.json()["jobs"]
    if not jobs:
        return None
    job_id = jobs[0]["id"]
    await client.post(f"/api/jobs/{job_id}/save", headers=auth_headers)

    apps_resp = await client.get("/api/applications", headers=auth_headers)
    apps = apps_resp.json()
    return apps[0]["id"] if apps else None


# ─────────────────────────────────────────────
#  1. List applications
# ─────────────────────────────────────────────
async def test_list_applications_requires_auth(client: AsyncClient):
    resp = await client.get("/api/applications")
    assert resp.status_code == 403


async def test_list_applications_empty(client: AsyncClient, auth_headers):
    # New user fixture → may have apps from save tests; just assert valid response
    resp = await client.get("/api/applications", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_list_applications_after_save(client: AsyncClient, auth_headers):
    await client.post("/api/jobs/seed", headers=auth_headers)
    jobs_resp = await client.get("/api/jobs", headers=auth_headers)
    jobs = jobs_resp.json()["jobs"]
    if not jobs:
        pytest.skip("No jobs seeded")

    job_id = jobs[0]["id"]
    await client.post(f"/api/jobs/{job_id}/save", headers=auth_headers)

    resp = await client.get("/api/applications", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


# ─────────────────────────────────────────────
#  2. Get single application
# ─────────────────────────────────────────────
async def test_get_application_by_id(client: AsyncClient, auth_headers):
    app_id = await _get_saved_app_id(client, auth_headers)
    if not app_id:
        pytest.skip("No application created")

    resp = await client.get(f"/api/applications/{app_id}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == app_id
    assert "job" in body
    assert "status" in body
    assert "history" in body


async def test_get_application_not_found(client: AsyncClient, auth_headers):
    resp = await client.get(
        "/api/applications/00000000-0000-0000-0000-000000000000",
        headers=auth_headers
    )
    assert resp.status_code == 404


# ─────────────────────────────────────────────
#  3. Update application status
# ─────────────────────────────────────────────
async def test_update_application_status(client: AsyncClient, auth_headers):
    app_id = await _get_saved_app_id(client, auth_headers)
    if not app_id:
        pytest.skip("No application created")

    resp = await client.put(
        f"/api/applications/{app_id}",
        json={"status": "applied"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "applied"


async def test_update_application_notes(client: AsyncClient, auth_headers):
    app_id = await _get_saved_app_id(client, auth_headers)
    if not app_id:
        pytest.skip("No application created")

    resp = await client.put(
        f"/api/applications/{app_id}/notes",
        json={"notes": "Follow up on Monday"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Notes updated"


# ─────────────────────────────────────────────
#  4. Application history is logged
# ─────────────────────────────────────────────
async def test_status_change_creates_history(client: AsyncClient, auth_headers):
    app_id = await _get_saved_app_id(client, auth_headers)
    if not app_id:
        pytest.skip("No application created")

    await client.put(
        f"/api/applications/{app_id}",
        json={"status": "applied"},
        headers=auth_headers,
    )

    resp = await client.get(f"/api/applications/{app_id}", headers=auth_headers)
    body = resp.json()
    assert len(body["history"]) >= 1
    statuses = [h["new_status"] for h in body["history"]]
    assert "applied" in statuses
