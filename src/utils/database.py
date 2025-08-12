from contextlib import contextmanager
from sqlmodel import Session, select
from src.models.model import ProcessStatus
from src.config.config import ENGINE
from datetime import datetime, timezone


# Get the Database Session
@contextmanager
def get_session():
    session = Session(ENGINE)
    try:
        yield session
    except Exception as e:
        print(f"DB error - {e}")
    finally:
        session.close()


# Record a starting process for any platform
def start_process(
    process_id: str,
    platform: str,
    prompt: str,
):
    with get_session() as session:
        item = ProcessStatus(
            process_id=process_id,
            status="running",
            platform=platform,
            prompt=prompt,
            start_time=datetime.now(timezone.utc),
            end_time=None,
        )
        session.add(item)
        session.commit()


# Update the process status while running
def update_process_status(
    process_id: str,
    status: str,
):
    with get_session() as session:
        stmt = select(ProcessStatus).where(ProcessStatus.process_id == process_id)
        process_status = session.exec(stmt).one_or_none()
        if process_status:
            process_status.status = status
            process_status.end_time = datetime.now(timezone.utc)
            session.commit()


# Retrieve a process status
def get_process_status(process_id: str):
    with get_session() as session:
        stmt = select(ProcessStatus).where(ProcessStatus.process_id == process_id)
        response = session.exec(stmt).one()
        if response:
            return response.status
    return None
