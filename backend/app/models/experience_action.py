
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ExperienceAction(Base):
    __tablename__ = "experience_actions"

    __table_args__ = (
        CheckConstraint(
            """
            outcome IN (
                'helped',
                'a_bit',
                'did_not_help'
            )
            OR outcome IS NULL
            """,
            name="valid_action_outcome"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    experience_id: Mapped[int] = mapped_column(
        ForeignKey("experiences.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    action_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    # NULL means the user has not answered the follow-up yet.
    outcome: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    outcome_recorded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    experience = relationship(
        "Experience",
        back_populates="actions"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
