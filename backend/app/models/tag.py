
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Tag(Base):
    __tablename__ = "tags"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "name",
            name="unique_user_tag"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = relationship("User", back_populates="tags")

    experience_tags = relationship(
        "ExperienceTag",
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
