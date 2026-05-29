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
