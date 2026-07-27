import logging
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.job import Job
from api.models.skill import Skill

logger = logging.getLogger(__name__)

EXPERIENCE_ORDER = ["Internship", "Junior", "Mid", "Mid-Senior", "Senior", "Lead", "Principal"]


async def get_recommendations(
    user_id: str,
    db: AsyncSession,
    limit: int = 10,
) -> list[dict]:
    profile_result = await db.execute(
        select(Skill).where(Skill.user_id == user_id)
    )
    skills = profile_result.scalars().all()

    from api.models.user import User
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    user_skill_names = [s.skill_name.lower() for s in skills]
    desired_role = (user.desired_role or "").lower()
    user_location = (user.location or "").lower()
    preferred_job_type = user.preferred_job_type or ""
    user_exp = user.years_of_experience or 0

    jobs_result = await db.execute(
        select(Job).where(Job.is_active == True).order_by(Job.posted_at.desc().nullslast())
    )
    jobs = jobs_result.scalars().all()

    scored = []
    for job in jobs:
        score, reasons = _score_job(job, user_skill_names, desired_role, user_location, preferred_job_type, user_exp)
        if score > 0:
            scored.append((score, reasons, job))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:limit]

    return [
        {
            "match_score": score,
            "match_reasons": reasons,
            "job": {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
                "requirements": job.requirements or [],
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_currency": job.salary_currency,
                "apply_url": job.apply_url,
                "job_type": job.job_type,
                "experience_level": job.experience_level,
                "posted_at": job.posted_at.isoformat() if job.posted_at else None,
            },
        }
        for score, reasons, job in top
    ]


def _score_job(job, user_skills, desired_role, user_location, preferred_job_type, user_exp):
    reasons = []
    score = 0
    max_score = 100

    skill_score = _compute_skill_match(job.requirements or [], user_skills)
    score += skill_score * 0.35
    if skill_score > 0:
        reasons.append(f"Matches {int(skill_score * 100)}% of your skills")

    title_score = _compute_title_match(job.title, desired_role)
    score += title_score * 0.20
    if title_score > 0.5:
        reasons.append(f"Aligns with your desired role: {job.title}")

    exp_score = _compute_experience_match(job.experience_level, user_exp)
    score += exp_score * 0.15
    if exp_score > 0.5:
        reasons.append("Experience level is a good fit")

    type_score = _compute_type_match(job.job_type, preferred_job_type)
    score += type_score * 0.15
    if type_score > 0.5:
        reasons.append(f"Matches your preferred work type ({job.job_type})")

    loc_score = _compute_location_match(job.location, user_location)
    score += loc_score * 0.15
    if loc_score > 0.5:
        reasons.append("Located in your area or remote-friendly")

    score = min(score, max_score)
    return int(score), reasons[:3]


def _compute_skill_match(required_skills, user_skills):
    if not required_skills:
        return 0.5
    if not user_skills:
        return 0
    required_lower = [s.lower() for s in required_skills]
    matched = sum(1 for rs in required_lower if rs in user_skills)
    return matched / len(required_skills)


def _compute_title_match(job_title, desired_role):
    if not desired_role:
        return 0.3
    job_lower = job_title.lower()
    desired_lower = desired_role.lower()

    if desired_lower in job_lower:
        return 1.0

    ratio = SequenceMatcher(None, job_lower, desired_lower).ratio()
    return min(ratio * 2, 0.8)


def _compute_experience_match(job_exp_level, user_exp):
    if not job_exp_level:
        return 0.5

    if job_exp_level == "Internship" and user_exp <= 1:
        return 1.0
    if job_exp_level == "Junior" and user_exp <= 3:
        return 1.0
    if job_exp_level == "Mid" and 2 <= user_exp <= 5:
        return 1.0
    if job_exp_level == "Mid-Senior" and 3 <= user_exp <= 7:
        return 1.0
    if job_exp_level == "Senior" and user_exp >= 5:
        return 1.0
    if job_exp_level == "Lead" and user_exp >= 7:
        return 1.0
    if job_exp_level == "Principal" and user_exp >= 10:
        return 1.0

    exp_order = EXPERIENCE_ORDER
    if job_exp_level in exp_order:
        idx = exp_order.index(job_exp_level)
        estimated = max(idx * 1.5, 1)
        diff = abs(user_exp - estimated)
        return max(0, 1 - diff * 0.15)

    return 0.5


def _compute_type_match(job_type, preferred_type):
    if not preferred_type:
        return 0.5
    if not job_type:
        return 0.5
    if job_type == preferred_type:
        return 1.0
    if preferred_type == "Remote" and job_type == "Hybrid":
        return 0.7
    if preferred_type == "Hybrid" and job_type == "Remote":
        return 0.7
    return 0.2


def _compute_location_match(job_location, user_location):
    if not job_location:
        return 0.3
    if "remote" in job_location.lower():
        return 1.0
    if not user_location:
        return 0.3
    city_user = user_location.split(",")[0].strip().lower()
    city_job = job_location.split(",")[0].strip().lower()
    if city_user == city_job:
        return 1.0
    if city_user in job_location.lower() or city_job in user_location.lower():
        return 0.8
    return 0.2
