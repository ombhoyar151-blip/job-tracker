from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user
from api.models.application import Application, ApplicationStatus
from api.models.resume import Resume

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def dashboard_stats(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    total_apps_result = await db.execute(
        select(func.count(Application.id)).where(Application.user_id == user_id)
    )
    total_apps = total_apps_result.scalar() or 0

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

    interview_result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == user_id,
            Application.status == ApplicationStatus.INTERVIEW_SCHEDULED,
        )
    )
    interview_count = interview_result.scalar() or 0

    offer_result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == user_id,
            Application.status == ApplicationStatus.OFFER_RECEIVED,
        )
    )
    offer_count = offer_result.scalar() or 0

    wishlist_result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == user_id,
            Application.status == ApplicationStatus.WISHLIST,
        )
    )
    wishlist_count = wishlist_result.scalar() or 0

    total_resumes_result = await db.execute(
        select(func.count(Resume.id)).where(Resume.user_id == user_id)
    )
    total_resumes = total_resumes_result.scalar() or 0

    return {
        "total_applications": total_apps,
        "active_applications": active_apps,
        "interviews_scheduled": interview_count,
        "offers_received": offer_count,
        "saved_jobs": wishlist_count,
        "resumes_uploaded": total_resumes,
    }
