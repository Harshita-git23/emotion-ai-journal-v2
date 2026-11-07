
from sqlalchemy import (
    String, Float, Boolean, ForeignKey, CheckConstraint
)
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

    emotion: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    # Model probability, stored between 0 and 1.
    # User-reported emotions have no probability score.
    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    is_confirmed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    experience = relationship(
        "Experience",
        back_populates="emotions"
    )
