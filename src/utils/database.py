from contextlib import contextmanager
from sqlmodel import Session, select
from src.models.model import ProcessStatus
from src.config.config import ENGINE


@contextmanager
def get_session():
    session = Session(ENGINE)
    try:
        yield session
    except Exception as e:
        print(f"DB error - {e}")
    finally:
        session.close()


def start_process(process_id: str, status: str = "running"):
    with get_session() as session:
        item = ProcessStatus(process_id=process_id, status=status)
        session.add(item)
        session.commit()


def update_process_status(process_id: str, status: str):
    with get_session() as session:
        stmt = select(ProcessStatus).where(ProcessStatus.process_id == process_id)
        process_status = session.exec(stmt).one()
        if process_status:
            process_status.process_id = process_id
            process_status.status = status
            session.commit()


def get_process_status(process_id: str):
    with get_session() as session:
        stmt = select(ProcessStatus).where(ProcessStatus.process_id == process_id)
        response = session.exec(stmt).one()
        if response:
            return response.status
    return None
