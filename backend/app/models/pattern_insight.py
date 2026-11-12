
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PatternInsight(Base):
    __tablename__ = "pattern_insights"

    __table_args__ = (
        CheckConstraint(
            """
            user_feedback IN (
                'unreviewed',
                'confirmed',
                'rejected'
            )
            """,
            name="valid_pattern_feedback"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    pattern_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Supporting counts, rates, sample sizes and other evidence.
    evidence: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    date_range_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    date_range_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    user_feedback: Mapped[str] = mapped_column(
        String(20),
        default="unreviewed",
        nullable=False
    )

    algorithm_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = relationship("User")
