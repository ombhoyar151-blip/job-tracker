import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Enum
from core.compat import GUID as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

import enum


class NotificationType(str, enum.Enum):
    INTERVIEW_REMINDER = "interview_reminder"
    APPLICATION_DEADLINE = "application_deadline"
    APPLICATION_STALE = "application_stale"
    NEW_MATCHED_JOBS = "new_matched_jobs"
    PROFILE_SUGGESTION = "profile_suggestion"
    STATUS_CHANGE = "status_change"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="notifications")
