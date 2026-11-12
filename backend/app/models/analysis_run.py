
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    __table_args__ = (
        CheckConstraint(
            "model_type IN ('text', 'speech')",
            name="valid_analysis_model_type"
        ),
        CheckConstraint(
            """
            status IN (
                'pending',
                'running',
                'completed',
                'failed',
                'skipped'
            )
            """,
            name="valid_analysis_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    experience_id: Mapped[int] = mapped_column(
        ForeignKey("experiences.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    content_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
        nullable=False
    )

    model_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    experience = relationship(
        "Experience",
        back_populates="analysis_runs"
    )

    emotion_observations = relationship(
        "EmotionObservation",
        back_populates="analysis_run"
    )
