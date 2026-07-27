from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user
from api.models.job import Job
from api.models.application import Application, ApplicationStatus
from api.services.job_seeds import get_mock_jobs
from api.ai.job_recommender import get_recommendations

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    requirements: list[str] = []
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    apply_url: str | None = None
    source: str | None = None
    job_type: str | None = None
    experience_level: str | None = None
    company_logo_url: str | None = None
    company_size: str | None = None
    posted_at: str | None = None
    is_saved: bool = False

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


EXPERIENCE_LEVELS = ["Internship", "Junior", "Mid", "Mid-Senior", "Senior", "Lead", "Principal"]
JOB_TYPES = ["Remote", "On-site", "Hybrid"]


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(Job.id)))
    count = result.scalar()
    if count and count > 0:
        return {"message": f"Database already has {count} jobs, skipping seed"}

    jobs_data = get_mock_jobs()
    for data in jobs_data:
        job = Job(**data)
        db.add(job)
    await db.commit()
    return {"message": f"Seeded {len(jobs_data)} jobs"}


@router.get("", response_model=JobListResponse)
async def list_jobs(
    q: str = Query("", description="Search query"),
    location: str = Query("", description="Filter by location"),
    job_type: str = Query("", description="Filter by job type"),
    experience_level: str = Query("", description="Filter by experience level"),
    salary_min: int = Query(0, description="Minimum salary"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Job).where(Job.is_active == True)

    if q:
        search = f"%{q}%"
        query = query.where(
            or_(
                Job.title.ilike(search),
                Job.company.ilike(search),
                Job.description.ilike(search),
            )
        )
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    if job_type and job_type in JOB_TYPES:
        query = query.where(Job.job_type == job_type)
    if experience_level and experience_level in EXPERIENCE_LEVELS:
        query = query.where(Job.experience_level == experience_level)
    if salary_min > 0:
        query = query.where(
            or_(Job.salary_max >= salary_min, Job.salary_min >= salary_min)
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Job.posted_at.desc().nullslast())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    jobs = result.scalars().all()

    saved_result = await db.execute(
        select(Application.job_id).where(
            Application.user_id == user_id,
            Application.status == ApplicationStatus.WISHLIST,
        )
    )
    saved_ids = {str(row[0]) for row in saved_result.all()}

    return JobListResponse(
        jobs=[
            JobResponse(
                id=str(job.id), title=job.title, company=job.company,
                location=job.location, description=job.description,
                requirements=job.requirements or [],
                salary_min=job.salary_min, salary_max=job.salary_max,
                salary_currency=job.salary_currency,
                apply_url=job.apply_url, source=job.source,
                job_type=job.job_type, experience_level=job.experience_level,
                company_logo_url=job.company_logo_url,
                company_size=job.company_size,
                posted_at=job.posted_at.isoformat() if job.posted_at else None,
                is_saved=str(job.id) in saved_ids,
            )
            for job in jobs
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id, Job.is_active == True))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    saved_result = await db.execute(
        select(Application).where(
            Application.user_id == user_id,
            Application.job_id == job_id,
            Application.status == ApplicationStatus.WISHLIST,
        )
    )
    is_saved = saved_result.scalar_one_or_none() is not None

    return JobResponse(
        id=str(job.id), title=job.title, company=job.company,
        location=job.location, description=job.description,
        requirements=job.requirements or [],
        salary_min=job.salary_min, salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        apply_url=job.apply_url, source=job.source,
        job_type=job.job_type, experience_level=job.experience_level,
        company_logo_url=job.company_logo_url,
        company_size=job.company_size,
        posted_at=job.posted_at.isoformat() if job.posted_at else None,
        is_saved=is_saved,
    )


@router.post("/{job_id}/save")
async def save_job(job_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id, Job.is_active == True))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    existing = await db.execute(
        select(Application).where(
            Application.user_id == user_id,
            Application.job_id == job_id,
        )
    )
    app = existing.scalar_one_or_none()
    if app:
        if app.status == ApplicationStatus.WISHLIST:
            return {"message": "Job already saved", "saved": True}
        app.status = ApplicationStatus.WISHLIST
        await db.commit()
        return {"message": "Job moved to wishlist", "saved": True}

    application = Application(
        user_id=user_id,
        job_id=job_id,
        status=ApplicationStatus.WISHLIST,
    )
    db.add(application)
    await db.flush()  # Assign application.id before referencing it in history

    from api.models.application import ApplicationHistory
    history = ApplicationHistory(
        application_id=application.id,
        new_status=ApplicationStatus.WISHLIST.value,
    )
    db.add(history)
    await db.commit()
    return {"message": "Job saved", "saved": True}


@router.post("/{job_id}/unsave")
async def unsave_job(job_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Application).where(
            Application.user_id == user_id,
            Application.job_id == job_id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        return {"message": "Job not saved", "saved": False}

    if app.status == ApplicationStatus.WISHLIST:
        await db.delete(app)
        await db.commit()
    
    return {"message": "Job unsaved", "saved": False}


class RecommendationItem(BaseModel):
    match_score: int
    match_reasons: list[str]
    job: JobResponse


@router.get("/recommendations", response_model=list[RecommendationItem])
async def recommended_jobs(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    recommendations = await get_recommendations(user_id, db)
    return [
        RecommendationItem(
            match_score=r["match_score"],
            match_reasons=r["match_reasons"],
            job=JobResponse(
                id=r["job"]["id"],
                title=r["job"]["title"],
                company=r["job"]["company"],
                location=r["job"]["location"],
                description=r["job"]["description"],
                requirements=r["job"]["requirements"],
                salary_min=r["job"]["salary_min"],
                salary_max=r["job"]["salary_max"],
                salary_currency=r["job"]["salary_currency"],
                apply_url=r["job"]["apply_url"],
                job_type=r["job"]["job_type"],
                experience_level=r["job"]["experience_level"],
                posted_at=r["job"]["posted_at"],
            ),
        )
        for r in recommendations
    ]
