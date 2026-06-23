from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user
from api.models.application import Application, ApplicationStatus
from api.models.skill import Skill
from api.models.job import Job

router = APIRouter(prefix="/api/insights", tags=["insights"])


class FunnelStep(BaseModel):
    status: str
    label: str
    count: int


class ApplicationTrend(BaseModel):
    month: str
    count: int


class SkillGap(BaseModel):
    skill: str
    demand_count: int


class InsightsResponse(BaseModel):
    funnel: list[FunnelStep]
    trends: list[ApplicationTrend]
    skill_gaps: list[SkillGap]
    interview_rate: float
    offer_rate: float
    active_applications: int
    total_applications: int


FUNNEL_LABELS = {
    ApplicationStatus.WISHLIST: "Saved",
    ApplicationStatus.APPLIED: "Applied",
    ApplicationStatus.UNDER_REVIEW: "Under Review",
    ApplicationStatus.INTERVIEW_SCHEDULED: "Interview",
    ApplicationStatus.OFFER_RECEIVED: "Offer",
    ApplicationStatus.REJECTED: "Rejected",
    ApplicationStatus.ACCEPTED: "Accepted",
    ApplicationStatus.WITHDRAWN: "Withdrawn",
}

FUNNEL_ORDER = [
    ApplicationStatus.WISHLIST,
    ApplicationStatus.APPLIED,
    ApplicationStatus.UNDER_REVIEW,
    ApplicationStatus.INTERVIEW_SCHEDULED,
    ApplicationStatus.OFFER_RECEIVED,
    ApplicationStatus.ACCEPTED,
    ApplicationStatus.REJECTED,
    ApplicationStatus.WITHDRAWN,
]


@router.get("", response_model=InsightsResponse)
async def get_insights(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(
        select(func.count(Application.id)).where(Application.user_id == user_id)
    )
    total_apps = total_result.scalar() or 0

    active_result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == user_id,
            Application.status.in_([
                ApplicationStatus.APPLIED,
                ApplicationStatus.UNDER_REVIEW,
                ApplicationStatus.INTERVIEW_SCHEDULED,
            ]),
        )
    )
    active_apps = active_result.scalar() or 0

    funnel_counts = {}
    for status_val in ApplicationStatus:
        cnt = await db.execute(
            select(func.count(Application.id))
            .where(Application.user_id == user_id, Application.status == status_val)
        )
        funnel_counts[status_val.value] = cnt.scalar() or 0

    funnel = [
        FunnelStep(
            status=s.value,
            label=FUNNEL_LABELS.get(s, s.value),
            count=funnel_counts.get(s.value, 0),
        )
        for s in FUNNEL_ORDER
    ]

    applied_count = funnel_counts.get(ApplicationStatus.APPLIED.value, 0) + \
                    funnel_counts.get(ApplicationStatus.UNDER_REVIEW.value, 0) + \
                    funnel_counts.get(ApplicationStatus.INTERVIEW_SCHEDULED.value, 0) + \
                    funnel_counts.get(ApplicationStatus.OFFER_RECEIVED.value, 0) + \
                    funnel_counts.get(ApplicationStatus.ACCEPTED.value, 0)
    interview_count = funnel_counts.get(ApplicationStatus.INTERVIEW_SCHEDULED.value, 0)
    offer_count = funnel_counts.get(ApplicationStatus.OFFER_RECEIVED.value, 0) + \
                  funnel_counts.get(ApplicationStatus.ACCEPTED.value, 0)

    interview_rate = round((interview_count / applied_count * 100), 1) if applied_count > 0 else 0
    offer_rate = round((offer_count / interview_count * 100), 1) if interview_count > 0 else 0

    months_back = 6
    trends = []
    for i in range(months_back - 1, -1, -1):
        dt = datetime.now(timezone.utc) - timedelta(days=30 * i)
        month_start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == months_back - 1:
            month_end = month_start
        else:
            next_dt = month_start + timedelta(days=32)
            month_end = next_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)

        cnt = await db.execute(
            select(func.count(Application.id))
            .where(
                Application.user_id == user_id,
                Application.created_at >= month_start,
                Application.created_at <= month_end,
            )
        )
        trends.append(ApplicationTrend(
            month=month_start.strftime("%b %Y"),
            count=cnt.scalar() or 0,
        ))

    skill_gaps_result = await db.execute(
        select(Skill.skill_name).where(Skill.user_id == user_id)
    )
    user_skills = {row[0].lower() for row in skill_gaps_result.fetchall()}

    jobs_result = await db.execute(
        select(Job.requirements).where(
            Job.is_active == True,
            Job.requirements.isnot(None),
        )
    )
    demand_counter = {}
    for row in jobs_result:
        reqs = row[0] or []
        for skill in reqs:
            skill_lower = skill.lower()
            if skill_lower not in user_skills:
                demand_counter[skill_lower] = demand_counter.get(skill_lower, 0) + 1

    sorted_gaps = sorted(demand_counter.items(), key=lambda x: x[1], reverse=True)[:10]
    skill_gaps = [SkillGap(skill=k, demand_count=v) for k, v in sorted_gaps]

    return InsightsResponse(
        funnel=funnel,
        trends=trends,
        skill_gaps=skill_gaps,
        interview_rate=interview_rate,
        offer_rate=offer_rate,
        active_applications=active_apps,
        total_applications=total_apps,
    )
