
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ExperienceTag(Base):
    __tablename__ = "experience_tags"

    experience_id: Mapped[int] = mapped_column(
        ForeignKey("experiences.id", ondelete="CASCADE"),
        primary_key=True
    )

    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )

    experience = relationship(
        "Experience",
        back_populates="experience_tags"
    )

    tag = relationship(
        "Tag",
        back_populates="experience_tags"
    )
