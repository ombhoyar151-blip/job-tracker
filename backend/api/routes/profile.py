from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user
from api.models.user import User
from api.models.skill import Skill
from api.models.education import Education
from api.models.work_experience import WorkExperience

router = APIRouter(prefix="/api/profile", tags=["profile"])


# --- Schemas ---

class ProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    location: str | None = None
    desired_role: str | None = None
    years_of_experience: int | None = None
    preferred_job_type: str | None = None
    bio: str | None = None
    skills: list[dict] = []
    education: list[dict] = []
    work_experiences: list[dict] = []

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    name: str | None = None
    location: str | None = None
    desired_role: str | None = None
    years_of_experience: int | None = None
    preferred_job_type: str | None = None
    bio: str | None = None


# --- Skills ---

class SkillCreate(BaseModel):
    skill_name: str
    proficiency_level: str | None = None


class SkillUpdate(BaseModel):
    skill_name: str | None = None
    proficiency_level: str | None = None


# --- Education ---

class EducationCreate(BaseModel):
    institution: str
    degree: str
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    grade: str | None = None
    description: str | None = None


class EducationUpdate(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool | None = None
    grade: str | None = None
    description: str | None = None


# --- Work Experience ---

class WorkCreate(BaseModel):
    company: str
    role: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None


class WorkUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool | None = None
    description: str | None = None


# --- Helpers ---

def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


async def _get_user(user_id: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- Profile Endpoints ---

@router.get("", response_model=ProfileResponse)
async def get_profile(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await _get_user(user_id, db)

    skills_result = await db.execute(select(Skill).where(Skill.user_id == user_id).order_by(Skill.skill_name))
    skills = [{"id": str(s.id), "skill_name": s.skill_name, "proficiency_level": s.proficiency_level} for s in skills_result.scalars().all()]

    edu_result = await db.execute(select(Education).where(Education.user_id == user_id).order_by(Education.start_date.desc().nullslast()))
    education = [{
        "id": str(e.id), "institution": e.institution, "degree": e.degree,
        "field_of_study": e.field_of_study,
        "start_date": e.start_date.isoformat() if e.start_date else None,
        "end_date": e.end_date.isoformat() if e.end_date else None,
        "is_current": e.is_current, "grade": e.grade, "description": e.description,
    } for e in edu_result.scalars().all()]

    work_result = await db.execute(select(WorkExperience).where(WorkExperience.user_id == user_id).order_by(WorkExperience.start_date.desc().nullslast()))
    work = [{
        "id": str(w.id), "company": w.company, "role": w.role,
        "location": w.location,
        "start_date": w.start_date.isoformat() if w.start_date else None,
        "end_date": w.end_date.isoformat() if w.end_date else None,
        "is_current": w.is_current, "description": w.description,
    } for w in work_result.scalars().all()]

    return ProfileResponse(
        id=str(user.id), name=user.name, email=user.email,
        location=user.location, desired_role=user.desired_role,
        years_of_experience=user.years_of_experience,
        preferred_job_type=user.preferred_job_type, bio=user.bio,
        skills=skills, education=education, work_experiences=work,
    )


@router.put("", response_model=ProfileResponse)
async def update_profile(req: UpdateProfileRequest, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await _get_user(user_id, db)
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)

    return await get_profile(user_id, db)


# --- Skills Endpoints ---

@router.post("/skills", status_code=status.HTTP_201_CREATED)
async def add_skill(req: SkillCreate, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Skill).where(Skill.user_id == user_id, Skill.skill_name.ilike(req.skill_name))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Skill already exists")

    skill = Skill(user_id=user_id, skill_name=req.skill_name, proficiency_level=req.proficiency_level)
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return {"id": str(skill.id), "skill_name": skill.skill_name, "proficiency_level": skill.proficiency_level}


@router.put("/skills/{skill_id}")
async def update_skill(skill_id: str, req: SkillUpdate, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill).where(Skill.id == skill_id, Skill.user_id == user_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(skill, key, value)
    await db.commit()
    await db.refresh(skill)
    return {"id": str(skill.id), "skill_name": skill.skill_name, "proficiency_level": skill.proficiency_level}


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill).where(Skill.id == skill_id, Skill.user_id == user_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    await db.delete(skill)
    await db.commit()


# --- Education Endpoints ---

@router.post("/education", status_code=status.HTTP_201_CREATED)
async def add_education(req: EducationCreate, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    edu = Education(
        user_id=user_id, institution=req.institution, degree=req.degree,
        field_of_study=req.field_of_study,
        start_date=_parse_date(req.start_date), end_date=_parse_date(req.end_date),
        is_current=req.is_current, grade=req.grade, description=req.description,
    )
    db.add(edu)
    await db.commit()
    await db.refresh(edu)
    return {"id": str(edu.id), "institution": edu.institution, "degree": edu.degree}


@router.put("/education/{edu_id}")
async def update_education(edu_id: str, req: EducationUpdate, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Education).where(Education.id == edu_id, Education.user_id == user_id))
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")
    update_data = req.model_dump(exclude_unset=True)
    if "start_date" in update_data:
        update_data["start_date"] = _parse_date(update_data["start_date"])
    if "end_date" in update_data:
        update_data["end_date"] = _parse_date(update_data["end_date"])
    for key, value in update_data.items():
        setattr(edu, key, value)
    await db.commit()
    await db.refresh(edu)
    return {"id": str(edu.id), "institution": edu.institution, "degree": edu.degree}


@router.delete("/education/{edu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(edu_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Education).where(Education.id == edu_id, Education.user_id == user_id))
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found")
    await db.delete(edu)
    await db.commit()


# --- Work Experience Endpoints ---

@router.post("/work", status_code=status.HTTP_201_CREATED)
async def add_work(req: WorkCreate, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    work = WorkExperience(
        user_id=user_id, company=req.company, role=req.role,
        location=req.location,
        start_date=_parse_date(req.start_date), end_date=_parse_date(req.end_date),
        is_current=req.is_current, description=req.description,
    )
    db.add(work)
    await db.commit()
    await db.refresh(work)
    return {"id": str(work.id), "company": work.company, "role": work.role}


@router.put("/work/{work_id}")
async def update_work(work_id: str, req: WorkUpdate, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkExperience).where(WorkExperience.id == work_id, WorkExperience.user_id == user_id))
    work = result.scalar_one_or_none()
    if not work:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work experience not found")
    update_data = req.model_dump(exclude_unset=True)
    if "start_date" in update_data:
        update_data["start_date"] = _parse_date(update_data["start_date"])
    if "end_date" in update_data:
        update_data["end_date"] = _parse_date(update_data["end_date"])
    for key, value in update_data.items():
        setattr(work, key, value)
    await db.commit()
    await db.refresh(work)
    return {"id": str(work.id), "company": work.company, "role": work.role}


@router.delete("/work/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work(work_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkExperience).where(WorkExperience.id == work_id, WorkExperience.user_id == user_id))
    work = result.scalar_one_or_none()
    if not work:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work experience not found")
    await db.delete(work)
    await db.commit()
