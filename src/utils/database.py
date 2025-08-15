from contextlib import contextmanager
from typing import Optional
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
            process_status.duration = (
                (process_status.end_time - process_status.start_time).total_seconds()
                if process_status.start_time
                else None
            )
            session.commit()


# Retrieve a process status
def get_process_status(process_id: str):
    with get_session() as session:
        stmt = select(ProcessStatus).where(ProcessStatus.process_id == process_id)
        response = session.exec(stmt).one()
        if response:
            return response.status
    return None


# Metrics - job success rate
def get_job_success_rate(platform: Optional[str], start_date: datetime):
    with get_session() as session:
        # Base queries
        query_total = select(ProcessStatus).where(
            ProcessStatus.start_time >= start_date
        )
        query_total = select(ProcessStatus).where(
            ProcessStatus.start_time >= start_date
        )
        query_success = select(ProcessStatus).where(
            ProcessStatus.start_time >= start_date, ProcessStatus.status == "success"
        )
        # Filter if per platform
        if platform:
            query_total = query_total.where(ProcessStatus.platform == platform)
            query_success = query_success.where(ProcessStatus.platform == platform)
        # Total Counts
        total_count = len(session.exec(query_total).all())
        success_count = len(session.exec(query_success).all())
        # Rate
        success_rate = (
            round((success_count / total_count) * 100, 2) if total_count else 0.0
        )
        success_rate = (
            round((success_count / total_count) * 100, 2) if total_count else 0.0
        )
    return {
        "platform": platform if platform else "all",
        "start_date": start_date,
        "total_jobs": total_count,
        "success_jobs": success_count,
        "success_rate_percent": success_rate,
    }


def get_average_job_duration(platform: Optional[str], start_date: datetime):
    with get_session() as session:
        query = select(ProcessStatus).where(ProcessStatus.start_time >= start_date)
        # Filter if per platform
        if platform:
            query = query.where(ProcessStatus.platform == platform)
        results = session.exec(query).all()
        durations = [r.duration for r in results if r.duration is not None]
        total_jobs = len(durations)
        avg_duration = round(sum(durations) / total_jobs, 2) if total_jobs else 0.0

    return {
        "platform": platform if platform else "all",
        "start_date": start_date,
        "total_jobs": total_jobs,
        "average_duration_seconds": avg_duration,
    }
