
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


class Experience(Base):
    __tablename__ = "experiences"

    __table_args__ = (
        CheckConstraint(
            "input_mode IN ('text', 'voice')",
            name="valid_experience_input_mode"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    # Free-writing content. May contain a voice transcript.
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Optional structured reflection fields.
    situation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    thoughts: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    input_mode: Mapped[str] = mapped_column(
        String(20),
        default="text",
        nullable=False
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="experiences"
    )

    emotion_observations = relationship(
        "EmotionObservation",
        back_populates="experience",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    analysis_runs = relationship(
        "AnalysisRun",
        back_populates="experience",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    voice_assets = relationship(
        "VoiceAsset",
        back_populates="experience",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    actions = relationship(
        "ExperienceAction",
        back_populates="experience",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    experience_tags = relationship(
        "ExperienceTag",
        back_populates="experience",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    content_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
        nullable=False
    )