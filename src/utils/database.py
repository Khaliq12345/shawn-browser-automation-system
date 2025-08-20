from contextlib import contextmanager
from typing import Optional
from sqlmodel import Session, select, col
from src.models.model import ProcessStatus
from src.config.config import ENGINE
from datetime import datetime, timezone
from sqlalchemy import desc


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
            if process_status.start_time.tzinfo is None:
                process_status.start_time = process_status.start_time.replace(tzinfo=timezone.utc)
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


#  -------- Metrics ----------
#
# Job Success Rate
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


# Avg Job Duration
def get_average_job_duration(platform: Optional[str], start_date: datetime):
    with get_session() as session:
        query = select(ProcessStatus).where(ProcessStatus.start_time >= start_date)
        # Filter if per platform
        if platform:
            query = query.where(ProcessStatus.platform == platform)
        results = session.exec(query).all()
        durations = [r.duration for r in results if r.duration is not None]
        avg_duration = round(sum(durations) / len(durations), 2) if durations else 0.0

    return {
        "platform": platform if platform else "all",
        "start_date": start_date,
        "total_jobs": len(durations),
        "average_duration_seconds": avg_duration,
    }


# Avg Total Time per Prompt
def get_average_total_time_per_prompt(start_date: datetime):
    with get_session() as session:
        query = select(ProcessStatus).where(ProcessStatus.start_time >= start_date)
        results = session.exec(query).all()
        durations = [r.duration for r in results if r.duration is not None]
        avg_time = round(sum(durations) / len(durations), 2) if durations else 0.0
        return {
            "platform": "all",
            "start_date": start_date,
            "total_jobs": len(durations),
            "average_total_time_seconds": avg_time,
        }


# Scraper Error Rate
def get_scraper_error_rate(start_date: datetime):
    with get_session() as session:
        query = select(ProcessStatus).where(ProcessStatus.start_time >= start_date)
        results = session.exec(query).all()
        total_runs = len(results)
        error_runs = sum(1 for r in results if r.status == "failed")
        rate = round(error_runs / total_runs, 2) if total_runs else 0.0
        return {
            "platform": "all",
            "start_date": start_date,
            "total_jobs": total_runs,
            "failed_jobs": error_runs,
            "scraper_error_rate": rate,
        }


# Prompt Coverage Rate
def get_prompt_coverage_rate(start_date: datetime):
    with get_session() as session:
        platforms = ["google", "chatgpt", "perplexity"]
        query = select(ProcessStatus).where(ProcessStatus.start_time >= start_date)
        results = session.exec(query).all()
        return_data = {
            "platform": "all",
            "start_date": start_date,
            "total_jobs": len(results),
        }
        # For each platform get the coverage
        for platform in platforms:
            platform_query = query.where(ProcessStatus.platform == platform)
            platform_results = session.exec(platform_query).all()
            coverage = (
                round(len(platform_results) / len(results), 2)
                if platform_results
                else 0.0
            )
            return_data[f"{platform}_jobs"] = len(platform_results)
            return_data[f"{platform}_coverage_rate"] = coverage
        return return_data


# Last Run Timestamp per Platform
def get_last_run_timestamp(platform: str):
    with get_session() as session:
        with get_session() as session:
            query = (
                select(ProcessStatus)
                .where(ProcessStatus.status == "success")
                .where(ProcessStatus.platform == platform)
                .order_by(desc(col(ProcessStatus.end_time)))
            )
            last_run = session.exec(query).first()
            return {
                "platform": platform,
                "last_successful_run": last_run.end_time if last_run else None,
            }


# Get all the process_id of a platform
def get_processes(platform: str) -> list[str]:
    with get_session() as session:
        query = select(ProcessStatus.process_id).where(
            ProcessStatus.platform == platform
        )
        results = session.exec(query).all()
        return [pid for pid in results if pid is not None]
