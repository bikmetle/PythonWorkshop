
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, sessionmaker
from sqlalchemy import String, Integer, DateTime
from datetime import datetime
from sqlalchemy import create_engine
engine = create_engine("sqlite:///chatbot.db", echo=True)

Session = sessionmaker(engine)

class Base(DeclarativeBase):
	pass

class Usage(Base):
	__tablename__ = "usages"

	id: Mapped[int] = mapped_column(primary_key=True)
	tg_id: Mapped[int] = mapped_column(Integer)
	created_at: Mapped[datetime] = mapped_column(DateTime)
	tokens: Mapped[int] = mapped_column(Integer)
    
Base.metadata.create_all(engine)