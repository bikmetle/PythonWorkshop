from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_engine("sqlite:///chatbot.db", echo=True)


class Base(DeclarativeBase):
    pass


class Usage(Base):
    __tablename__ = "usage"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    tokens: Mapped[int | None]
