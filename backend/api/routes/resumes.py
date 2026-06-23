import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import get_db
from core.dependencies import get_current_user
from api.models.resume import Resume
from api.models.ai_analysis import AIAnalysis
from api.services.resume_parser import extract_text
from api.ai.resume_analyzer import analyze_resume

router = APIRouter(prefix="/api/resumes", tags=["resumes"])
settings = get_settings()

ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}
MAX_FILE_SIZE = 10 * 1024 * 1024


class ResumeResponse(BaseModel):
    id: str
    file_name: str
    file_type: str
    uploaded_at: str
    version: int
    is_active: bool
    has_analysis: bool = False

    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    id: str
    resume_id: str
    strengths: list[str] = []
    weaknesses: list[str] = []
    missing_skills: list[str] = []
    recommendations: list[str] = []
    ats_score: int | None = None
    suggested_roles: list[str] = []
    created_at: str

    class Config:
        from_attributes = True


async def save_upload(file: UploadFile, user_id: str) -> str:
    ext = ALLOWED_TYPES.get(file.content_type, "")
    filename = f"{user_id}/{uuid.uuid4()}{ext}"
    abs_path = os.path.join(settings.upload_dir, filename)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large (max 10MB)")

    with open(abs_path, "wb") as f:
        f.write(contents)

    return filename


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...), user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF and DOCX files are allowed")

    file_path = await save_upload(file, user_id)

    count_result = await db.execute(select(Resume).where(Resume.user_id == user_id, Resume.is_active == True))
    current_active = count_result.scalars().all()
    for r in current_active:
        r.is_active = False

    version = (max((r.version for r in current_active), default=0)) + 1

    resume = Resume(
        user_id=user_id,
        file_url=file_path,
        file_name=file.filename,
        file_type=file.content_type,
        is_active=True,
        version=version,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return ResumeResponse(
        id=str(resume.id), file_name=resume.file_name,
        file_type=resume.file_type,
        uploaded_at=resume.uploaded_at.isoformat(),
        version=resume.version, is_active=resume.is_active,
    )


@router.get("", response_model=list[ResumeResponse])
async def list_resumes(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id).order_by(Resume.uploaded_at.desc())
    )
    resumes = result.scalars().all()

    analysis_result = await db.execute(
        select(AIAnalysis.resume_id).where(
            AIAnalysis.resume_id.in_([r.id for r in resumes])
        )
    )
    analyzed_ids = {str(row[0]) for row in analysis_result.all()}

    return [
        ResumeResponse(
            id=str(r.id), file_name=r.file_name, file_type=r.file_type,
            uploaded_at=r.uploaded_at.isoformat(), version=r.version,
            is_active=r.is_active, has_analysis=str(r.id) in analyzed_ids,
        )
        for r in resumes
    ]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    analysis_result = await db.execute(
        select(AIAnalysis).where(AIAnalysis.resume_id == resume_id)
    )
    has_analysis = analysis_result.first() is not None

    return ResumeResponse(
        id=str(resume.id), file_name=resume.file_name, file_type=resume.file_type,
        uploaded_at=resume.uploaded_at.isoformat(), version=resume.version,
        is_active=resume.is_active, has_analysis=has_analysis,
    )


@router.post("/{resume_id}/analyze", response_model=AnalysisResponse)
async def analyze_resume_endpoint(resume_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    existing_result = await db.execute(
        select(AIAnalysis).where(AIAnalysis.resume_id == resume_id).order_by(AIAnalysis.created_at.desc())
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        return AnalysisResponse(
            id=str(existing.id), resume_id=str(existing.resume_id),
            strengths=existing.strengths or [],
            weaknesses=existing.weaknesses or [],
            missing_skills=existing.missing_skills or [],
            recommendations=existing.recommendations or [],
            ats_score=existing.ats_score,
            suggested_roles=existing.suggested_roles or [],
            created_at=existing.created_at.isoformat(),
        )

    abs_path = os.path.join(settings.upload_dir, resume.file_url)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found on disk")

    try:
        text = extract_text(abs_path, resume.file_type)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to parse resume: {e}")

    try:
        analysis = await analyze_resume(text)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI analysis failed: {e}")

    ai_analysis = AIAnalysis(
        resume_id=resume_id,
        strengths=analysis.get("strengths", []),
        weaknesses=analysis.get("weaknesses", []),
        missing_skills=analysis.get("missing_skills", []),
        recommendations=analysis.get("recommendations", []),
        ats_score=analysis.get("ats_score"),
        suggested_roles=analysis.get("suggested_roles", []),
        raw_analysis=analysis,
        model_used="gemini-1.5-flash" if settings.gemini_api_key else "mock",
        analysis_version="1.0",
    )
    db.add(ai_analysis)
    await db.commit()
    await db.refresh(ai_analysis)

    return AnalysisResponse(
        id=str(ai_analysis.id), resume_id=str(ai_analysis.resume_id),
        strengths=ai_analysis.strengths or [],
        weaknesses=ai_analysis.weaknesses or [],
        missing_skills=ai_analysis.missing_skills or [],
        recommendations=ai_analysis.recommendations or [],
        ats_score=ai_analysis.ats_score,
        suggested_roles=ai_analysis.suggested_roles or [],
        created_at=ai_analysis.created_at.isoformat(),
    )


@router.get("/{resume_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(resume_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    analysis_result = await db.execute(
        select(AIAnalysis).where(AIAnalysis.resume_id == resume_id).order_by(AIAnalysis.created_at.desc())
    )
    analysis = analysis_result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found for this resume")

    return AnalysisResponse(
        id=str(analysis.id), resume_id=str(analysis.resume_id),
        strengths=analysis.strengths or [],
        weaknesses=analysis.weaknesses or [],
        missing_skills=analysis.missing_skills or [],
        recommendations=analysis.recommendations or [],
        ats_score=analysis.ats_score,
        suggested_roles=analysis.suggested_roles or [],
        created_at=analysis.created_at.isoformat(),
    )
