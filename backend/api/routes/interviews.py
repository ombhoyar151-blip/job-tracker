from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db
from core.dependencies import get_current_user
from api.models.interview import Interview, InterviewRoundType, InterviewOutcome
from api.models.application import Application
from api.models.job import Job
from api.ai.interview_prep import generate_questions

router = APIRouter(prefix="/api/interviews", tags=["interviews"])


class InterviewCreate(BaseModel):
    application_id: str
    scheduled_at: str | None = None
    round_type: InterviewRoundType = InterviewRoundType.PHONE
    interview_format: str | None = None
    location_or_link: str | None = None
    interviewer_name: str | None = None
    interviewer_role: str | None = None
    notes: str | None = None


class InterviewUpdate(BaseModel):
    scheduled_at: str | None = None
    round_type: InterviewRoundType | None = None
    interview_format: str | None = None
    location_or_link: str | None = None
    interviewer_name: str | None = None
    interviewer_role: str | None = None
    notes: str | None = None
    outcome: InterviewOutcome | None = None


class InterviewResponse(BaseModel):
    id: str
    application_id: str
    scheduled_at: str | None = None
    round_type: InterviewRoundType
    interview_format: str | None = None
    location_or_link: str | None = None
    interviewer_name: str | None = None
    interviewer_role: str | None = None
    notes: str | None = None
    outcome: InterviewOutcome
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/application/{application_id}", response_model=list[InterviewResponse])
async def list_interviews(
    application_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app_result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user_id,
        )
    )
    app = app_result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    result = await db.execute(
        select(Interview)
        .where(Interview.application_id == application_id)
        .order_by(Interview.scheduled_at.asc().nullslast(), Interview.created_at.desc())
    )
    interviews = result.scalars().all()

    return [
        InterviewResponse(
            id=str(iv.id),
            application_id=str(iv.application_id),
            scheduled_at=iv.scheduled_at.isoformat() if iv.scheduled_at else None,
            round_type=iv.round_type,
            interview_format=iv.interview_format,
            location_or_link=iv.location_or_link,
            interviewer_name=iv.interviewer_name,
            interviewer_role=iv.interviewer_role,
            notes=iv.notes,
            outcome=iv.outcome,
            created_at=iv.created_at.isoformat(),
            updated_at=iv.updated_at.isoformat(),
        )
        for iv in interviews
    ]


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    body: InterviewCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app_result = await db.execute(
        select(Application).where(
            Application.id == body.application_id,
            Application.user_id == user_id,
        )
    )
    app = app_result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    scheduled = None
    if body.scheduled_at:
        scheduled = datetime.fromisoformat(body.scheduled_at)

    interview = Interview(
        application_id=app.id,
        scheduled_at=scheduled,
        round_type=body.round_type,
        interview_format=body.interview_format,
        location_or_link=body.location_or_link,
        interviewer_name=body.interviewer_name,
        interviewer_role=body.interviewer_role,
        notes=body.notes,
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)

    return InterviewResponse(
        id=str(interview.id),
        application_id=str(interview.application_id),
        scheduled_at=interview.scheduled_at.isoformat() if interview.scheduled_at else None,
        round_type=interview.round_type,
        interview_format=interview.interview_format,
        location_or_link=interview.location_or_link,
        interviewer_name=interview.interviewer_name,
        interviewer_role=interview.interviewer_role,
        notes=interview.notes,
        outcome=interview.outcome,
        created_at=interview.created_at.isoformat(),
        updated_at=interview.updated_at.isoformat(),
    )


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: str,
    body: InterviewUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Interview)
        .options(selectinload(Interview.application))
        .where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    if not interview or interview.application.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    if body.scheduled_at is not None:
        interview.scheduled_at = datetime.fromisoformat(body.scheduled_at)
    if body.round_type is not None:
        interview.round_type = body.round_type
    if body.interview_format is not None:
        interview.interview_format = body.interview_format
    if body.location_or_link is not None:
        interview.location_or_link = body.location_or_link
    if body.interviewer_name is not None:
        interview.interviewer_name = body.interviewer_name
    if body.interviewer_role is not None:
        interview.interviewer_role = body.interviewer_role
    if body.notes is not None:
        interview.notes = body.notes
    if body.outcome is not None:
        interview.outcome = body.outcome

    await db.commit()
    await db.refresh(interview)

    return InterviewResponse(
        id=str(interview.id),
        application_id=str(interview.application_id),
        scheduled_at=interview.scheduled_at.isoformat() if interview.scheduled_at else None,
        round_type=interview.round_type,
        interview_format=interview.interview_format,
        location_or_link=interview.location_or_link,
        interviewer_name=interview.interviewer_name,
        interviewer_role=interview.interviewer_role,
        notes=interview.notes,
        outcome=interview.outcome,
        created_at=interview.created_at.isoformat(),
        updated_at=interview.updated_at.isoformat(),
    )


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(
    interview_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Interview)
        .options(selectinload(Interview.application))
        .where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    if not interview or interview.application.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    await db.delete(interview)
    await db.commit()


class PrepQuestion(BaseModel):
    question: str
    type: str
    focus_area: str
    suggested_answer: str


class PrepResponse(BaseModel):
    role: str
    questions: list[PrepQuestion]


@router.get("/prep/{application_id}", response_model=PrepResponse)
async def generate_interview_prep(
    application_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.job))
        .where(Application.id == application_id, Application.user_id == user_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    job = app.job
    data = await generate_questions(
        job_title=job.title,
        description=job.description or "",
        skills=job.requirements or [],
    )

    return PrepResponse(
        role=data.get("role", job.title),
        questions=[PrepQuestion(**q) for q in data.get("questions", [])],
    )
