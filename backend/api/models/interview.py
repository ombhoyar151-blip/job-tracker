import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from core.compat import GUID as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

import enum


class InterviewRoundType(str, enum.Enum):
    PHONE = "phone"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    ONSITE = "onsite"
    PANEL = "panel"
    TAKE_HOME = "take_home"
    FINAL = "final"


class InterviewOutcome(str, enum.Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    round_type: Mapped[InterviewRoundType] = mapped_column(
        default=InterviewRoundType.PHONE
    )
    interview_format: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location_or_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    interviewer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    interviewer_role: Mapped[str | None] = mapped_column(String(255), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[InterviewOutcome] = mapped_column(default=InterviewOutcome.PENDING)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates="interviews")
