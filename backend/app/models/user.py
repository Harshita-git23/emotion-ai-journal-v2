
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    experiences = relationship(
        "Experience",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    tags = relationship(
        "Tag",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
