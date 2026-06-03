from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

engine = create_engine("sqlite:///chatbot.db", echo=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String)

    usages: Mapped[List["Usage"]] = relationship(back_populates="user")


class Usage(Base):
    __tablename__ = "usages"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    tokens: Mapped[int | None]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="usages")
