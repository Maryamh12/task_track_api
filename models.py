from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database import Base


class Task(Base):

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    owner: Mapped["User"] = relationship(
        back_populates= "tasks"
    )


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    hashed_password: Mapped[str] =mapped_column(
        String(255),
        nullable=False
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates= "owner"
    )

