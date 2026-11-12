
from sqlalchemy import (
    String,
    Float,
    ForeignKey,
    CheckConstraint,
    DateTime
)
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class EmotionObservation(Base):
    __tablename__ = "emotion_observations"

    __table_args__ = (
        CheckConstraint(
            "source IN ('user_reported', 'text_model', 'speech_model')",
            name="valid_emotion_source"
        ),
        CheckConstraint(
            """
            feedback_status IN (
                'not_applicable',
                'pending',
                'confirmed',
                'rejected'
            )
            """,
            name="valid_feedback_status"
        ),
        CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 1)",
            name="valid_emotion_score"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    experience_id: Mapped[int] = mapped_column(
        ForeignKey("experiences.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Nullable for emotions reported directly by the user.
    analysis_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    emotion: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    feedback_status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    experience = relationship(
        "Experience",
        back_populates="emotion_observations"
    )

    analysis_run = relationship(
        "AnalysisRun",
        back_populates="emotion_observations"
    )
