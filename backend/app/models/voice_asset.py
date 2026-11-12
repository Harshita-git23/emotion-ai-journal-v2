
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class VoiceAsset(Base):
    __tablename__ = "voice_assets"

    __table_args__ = (
        CheckConstraint(
            "file_size_bytes > 0",
            name="valid_audio_file_size"
        ),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="valid_audio_duration"
        ),
        CheckConstraint(
            """
            transcription_status IN (
                'pending',
                'completed',
                'failed',
                'skipped'
            )
            """,
            name="valid_transcription_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    experience_id: Mapped[int] = mapped_column(
        ForeignKey("experiences.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Private storage location, not a public URL.
    storage_key: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False
    )

    original_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    transcript: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    transcription_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    retention_consent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    experience = relationship(
        "Experience",
        back_populates="voice_assets"
    )
