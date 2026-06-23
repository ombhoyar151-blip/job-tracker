from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db
from core.dependencies import get_current_user
from api.models.application import Application, ApplicationHistory, ApplicationStatus
from api.models.job import Job

router = APIRouter(prefix="/api/applications", tags=["applications"])


class ApplicationJob(BaseModel):
    id: str
    title: str
    company: str
    location: str | None = None


class ApplicationListItem(BaseModel):
    id: str
    job: ApplicationJob
    status: ApplicationStatus
    notes: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    applied_at: str | None = None
    created_at: str
    updated_at: str


class ApplicationUpdateRequest(BaseModel):
    status: ApplicationStatus | None = None
    notes: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None


class HistoryItem(BaseModel):
    id: str
    old_status: str | None = None
    new_status: str
    changed_at: str
    notes: str | None = None


class ApplicationDetail(BaseModel):
    id: str
    job: ApplicationJob
    status: ApplicationStatus
    notes: str | None = None
    cover_letter_url: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    applied_at: str | None = None
    created_at: str
    updated_at: str
    history: list[HistoryItem]


@router.get("", response_model=list[ApplicationListItem])
async def list_applications(
    status: ApplicationStatus | None = Query(None),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Application)
        .options(selectinload(Application.job))
        .where(Application.user_id == user_id)
    )
    if status:
        query = query.where(Application.status == status)
    query = query.order_by(Application.updated_at.desc())

    result = await db.execute(query)
    apps = result.scalars().all()

    return [
        ApplicationListItem(
            id=str(app.id),
            job=ApplicationJob(
                id=str(app.job.id),
                title=app.job.title,
                company=app.job.company,
                location=app.job.location,
            ),
            status=app.status,
            notes=app.notes,
            contact_name=app.contact_name,
            contact_email=app.contact_email,
            applied_at=app.applied_at.isoformat() if app.applied_at else None,
            created_at=app.created_at.isoformat(),
            updated_at=app.updated_at.isoformat(),
        )
        for app in apps
    ]


@router.get("/{application_id}", response_model=ApplicationDetail)
async def get_application(
    application_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.job), selectinload(Application.history))
        .where(Application.id == application_id, Application.user_id == user_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    return ApplicationDetail(
        id=str(app.id),
        job=ApplicationJob(
            id=str(app.job.id),
            title=app.job.title,
            company=app.job.company,
            location=app.job.location,
        ),
        status=app.status,
        notes=app.notes,
        cover_letter_url=app.cover_letter_url,
        contact_name=app.contact_name,
        contact_email=app.contact_email,
        applied_at=app.applied_at.isoformat() if app.applied_at else None,
        created_at=app.created_at.isoformat(),
        updated_at=app.updated_at.isoformat(),
        history=[
            HistoryItem(
                id=str(h.id),
                old_status=h.old_status,
                new_status=h.new_status,
                changed_at=h.changed_at.isoformat(),
                notes=h.notes,
            )
            for h in app.history
        ],
    )


@router.put("/{application_id}", response_model=ApplicationDetail)
async def update_application(
    application_id: str,
    body: ApplicationUpdateRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.job), selectinload(Application.history))
        .where(Application.id == application_id, Application.user_id == user_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    old_status = app.status.value if app.status else None
    changed = False

    if body.status is not None and body.status != app.status:
        app.status = body.status
        changed = True
        if body.status == ApplicationStatus.APPLIED and not app.applied_at:
            app.applied_at = datetime.now(timezone.utc)

    if body.notes is not None and body.notes != app.notes:
        app.notes = body.notes
        changed = True

    if body.contact_name is not None:
        app.contact_name = body.contact_name
        changed = True

    if body.contact_email is not None:
        app.contact_email = body.contact_email
        changed = True

    if changed:
        history = ApplicationHistory(
            application_id=app.id,
            old_status=old_status,
            new_status=app.status.value,
            notes=body.notes if body.notes != app.notes else None,
        )
        db.add(history)
        await db.commit()
        await db.refresh(app)

    return ApplicationDetail(
        id=str(app.id),
        job=ApplicationJob(
            id=str(app.job.id),
            title=app.job.title,
            company=app.job.company,
            location=app.job.location,
        ),
        status=app.status,
        notes=app.notes,
        cover_letter_url=app.cover_letter_url,
        contact_name=app.contact_name,
        contact_email=app.contact_email,
        applied_at=app.applied_at.isoformat() if app.applied_at else None,
        created_at=app.created_at.isoformat(),
        updated_at=app.updated_at.isoformat(),
        history=[
            HistoryItem(
                id=str(h.id),
                old_status=h.old_status,
                new_status=h.new_status,
                changed_at=h.changed_at.isoformat(),
                notes=h.notes,
            )
            for h in app.history
        ],
    )


@router.put("/{application_id}/notes")
async def update_notes(
    application_id: str,
    body: dict,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user_id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    notes = body.get("notes")
    app.notes = notes
    await db.commit()

    return {"message": "Notes updated"}
