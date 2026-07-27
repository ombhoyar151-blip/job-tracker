import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from core.compat import GUID as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

import enum


class ApplicationStatus(str, enum.Enum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    OFFER_RECEIVED = "offer_received"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.WISHLIST,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_letter_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")
    history = relationship("ApplicationHistory", back_populates="application", cascade="all, delete-orphan", order_by="ApplicationHistory.changed_at.desc()")


class ApplicationHistory(Base):
    __tablename__ = "application_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    application = relationship("Application", back_populates="history")
