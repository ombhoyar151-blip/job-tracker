"""
Tests for: /api/profile, /api/dashboard/stats, /api/notifications, /api/insights
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ─────────────────────────────────────────────
#  1. Get profile
# ─────────────────────────────────────────────
async def test_get_profile_requires_auth(client: AsyncClient):
    resp = await client.get("/api/profile")
    assert resp.status_code == 403


async def test_get_profile(client: AsyncClient, auth_headers):
    resp = await client.get("/api/profile", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "email" in body
    assert "name" in body


# ─────────────────────────────────────────────
#  2. Update basic profile
# ─────────────────────────────────────────────
async def test_update_profile(client: AsyncClient, auth_headers):
    resp = await client.put("/api/profile", json={
        "location": "Bangalore, India",
        "bio": "Passionate about building scalable systems.",
        "desired_role": "Senior Python Developer",
    }, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["location"] == "Bangalore, India"


# ─────────────────────────────────────────────
#  3. Dashboard endpoint  (route: /api/dashboard/stats)
# ─────────────────────────────────────────────
async def test_dashboard_requires_auth(client: AsyncClient):
    resp = await client.get("/api/dashboard/stats")
    assert resp.status_code == 403


async def test_dashboard(client: AsyncClient, auth_headers):
    resp = await client.get("/api/dashboard/stats", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "total_applications" in body
    assert "active_applications" in body
    assert "offers_received" in body


# ─────────────────────────────────────────────
#  4. Notifications endpoint
# ─────────────────────────────────────────────
async def test_list_notifications_requires_auth(client: AsyncClient):
    resp = await client.get("/api/notifications")
    assert resp.status_code == 403


async def test_list_notifications(client: AsyncClient, auth_headers):
    resp = await client.get("/api/notifications", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_unread_notifications_count(client: AsyncClient, auth_headers):
    resp = await client.get("/api/notifications/unread", headers=auth_headers)
    assert resp.status_code == 200
    assert "unread_count" in resp.json()


# ─────────────────────────────────────────────
#  5. Insights endpoint
# ─────────────────────────────────────────────
async def test_insights_requires_auth(client: AsyncClient):
    resp = await client.get("/api/insights")
    assert resp.status_code == 403


async def test_insights(client: AsyncClient, auth_headers):
    resp = await client.get("/api/insights", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "funnel" in body
    assert "trends" in body
    assert "total_applications" in body
    assert "interview_rate" in body


# ─────────────────────────────────────────────
#  6. Profile skills CRUD
# ─────────────────────────────────────────────
async def test_add_skill(client: AsyncClient, auth_headers):
    resp = await client.post("/api/profile/skills", json={
        "skill_name": "Python",
        "proficiency_level": "Advanced"
    }, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["skill_name"] == "Python"


async def test_add_duplicate_skill(client: AsyncClient, auth_headers):
    await client.post("/api/profile/skills", json={"skill_name": "Java"}, headers=auth_headers)
    resp = await client.post("/api/profile/skills", json={"skill_name": "Java"}, headers=auth_headers)
    assert resp.status_code == 409


# ─────────────────────────────────────────────
#  7. Profile education CRUD
# ─────────────────────────────────────────────
async def test_add_education(client: AsyncClient, auth_headers):
    resp = await client.post("/api/profile/education", json={
        "institution": "IIT Delhi",
        "degree": "B.Tech",
        "field_of_study": "Computer Science",
        "start_date": "2019-07-01",
        "end_date": "2023-05-31",
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["institution"] == "IIT Delhi"


# ─────────────────────────────────────────────
#  8. Profile work experience CRUD
# ─────────────────────────────────────────────
async def test_add_work_experience(client: AsyncClient, auth_headers):
    resp = await client.post("/api/profile/work", json={
        "company": "Google",
        "role": "Software Engineer",
        "location": "Remote",
        "start_date": "2023-06-01",
        "is_current": True,
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["company"] == "Google"
