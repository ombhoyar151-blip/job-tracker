import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from core.compat import GUID as UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)

    strengths: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    weaknesses: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    missing_skills: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    ats_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    suggested_roles: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    raw_analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    analysis_version: Mapped[str | None] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="analyses")
