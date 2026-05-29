from sqlalchemy import select

from models import Session, Usage


def add_usage(usage: Usage) -> None:
    with Session() as session:
        try:
            session.add(usage)
        except Exception:
            session.rollback()
            raise
        else:
            session.commit()

def get_usage(tg_id: int) -> int:
    statement = select(Usage).where(Usage.tg_id == tg_id)

    with Session() as session:
        db_objects = session.scalars(statement).all()

    return sum(row.tokens for row in db_objects)