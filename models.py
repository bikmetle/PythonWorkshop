from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_engine("sqlite:///chatbot.db", echo=True)


class Base(DeclarativeBase):
    pass


class Usage(Base):
    __tablename__ = "usage"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    tokens: Mapped[int | None]


# Create all tables in the engine
Base.metadata.create_all(engine)
