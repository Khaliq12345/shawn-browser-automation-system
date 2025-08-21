from typing import Optional
from sqlmodel import select, text
from src.models.model import Processes, get_engine
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import async_sessionmaker


# Record a starting process for any platform
async def start_process(
    process_id: str,
    platform: str,
    prompt: str,
):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        item = Processes(
            process_id=process_id,
            status="running",
            platform=platform,
            prompt=prompt,
            start_time=datetime.now(timezone.utc),
            end_time=None,
        )
        session.add(item)
        await session.commit()
    await engine.dispose()


# Update the process status while running
async def update_process_status(
    process_id: str,
    status: str,
):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = select(Processes).where(Processes.process_id == process_id)
        process = await session.execute(stmt)
        process = process.one_or_none()
        if process:
            process.status = status
            process.end_time = datetime.now(timezone.utc)
            if process.start_time.tzinfo is None:
                process.start_time = process.start_time.replace(tzinfo=timezone.utc)
            process.duration = (
                (process.end_time - process.start_time).total_seconds()
                if process.start_time
                else None
            )
            await session.commit()
    await engine.dispose()


# Retrieve a process status
async def get_process_status(process_id: str):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = select(Processes).where(Processes.process_id == process_id)
        process = await session.execute(stmt)
        process = process.one_or_none()
        if process:
            return process.status
    await engine.dispose()
    return None


#  -------- Metrics ----------


# Job Success Rate
async def get_job_success_rate(start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    combined_data = []
    async with async_session() as session:
        stmt = f"""
        SELECT 
            COUNT(*) AS total_jobs,
            COALESCE(platform, 'all') AS platform,
            COUNT(CASE WHEN status = 'success' THEN 1 END) AS success_jobs,
            ((COUNT(CASE WHEN status = 'success' THEN 1 END)::float / COUNT(*)) * 100) AS success_rate
        FROM processes
        WHERE start_time > '{start_date}'
        GROUP BY ROLLUP(platform)
        """
        success_table = await session.execute(text(stmt))
        keys = success_table.keys()
        values = success_table.fetchall()
        combined_data = [dict(zip(keys, row)) for row in values]
    await engine.dispose()
    return combined_data


# Avg Job Duration
async def get_average_job_duration(platform: Optional[str], start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = f"""
        SELECT 
            COUNT(duration) AS total_jobs,
            COALESCE(AVG(duration), 0) AS average_duration_seconds
        FROM processes
        WHERE start_time >= '{start_date}'
        {f"AND platform = '{platform}'" if platform else ""}
        """
        result = await session.execute(text(stmt))
        row = result.fetchone()
        return {
            "platform": platform if platform else "all",
            "start_date": start_date,
            "total_jobs": row.total_jobs if row else 0,
            "average_duration_seconds": round(row.average_duration_seconds, 2)
            if row
            else 0.0,
        }


# Avg Total Time per Prompt
async def get_average_total_time_per_prompt(start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = f"""
        SELECT 
            COUNT(duration) AS total_jobs,
            COALESCE(AVG(duration), 0) AS average_total_time_seconds
        FROM processes
        WHERE start_time >= '{start_date}'
        """
        result = await session.execute(text(stmt))
        row = result.fetchone()
        return {
            "platform": "all",
            "start_date": start_date,
            "total_jobs": row.total_jobs if row else 0,
            "average_total_time_seconds": round(row.average_total_time_seconds, 2)
            if row
            else 0.0,
        }


# Scraper Error Rate
async def get_scraper_error_rate(start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = f"""
        SELECT 
            COUNT(*) AS total_jobs,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) AS failed_jobs
        FROM processes
        WHERE start_time >= '{start_date}'
        """
        result = await session.execute(text(stmt))
        row = result.fetchone()
        total_jobs = row.total_jobs if row else 0
        failed_jobs = row.failed_jobs if row else 0
        return {
            "platform": "all",
            "start_date": start_date,
            "total_jobs": total_jobs,
            "failed_jobs": failed_jobs,
            "scraper_error_rate": round(failed_jobs / total_jobs, 2)
            if total_jobs
            else 0.0,
        }


# Prompt Coverage Rate
async def get_prompt_coverage_rate(start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        platforms = ["google", "chatgpt", "perplexity"]

        stmt_all = f"""
        SELECT COUNT(*) AS total_jobs
        FROM processes
        WHERE start_time >= '{start_date}'
        """
        all_result = await session.execute(text(stmt_all))
        all_jobs = all_result.scalar() or 0

        return_data = {
            "platform": "all",
            "start_date": start_date,
            "total_jobs": all_jobs,
        }

        for platform in platforms:
            stmt_platform = f"""
            SELECT COUNT(*) AS platform_jobs
            FROM processes
            WHERE start_time >= '{start_date}' AND platform = '{platform}'
            """
            result = await session.execute(text(stmt_platform))
            platform_jobs = result.scalar() or 0
            coverage = round(platform_jobs / all_jobs, 2) if all_jobs else 0.0
            return_data[f"{platform}_jobs"] = platform_jobs
            return_data[f"{platform}_coverage_rate"] = coverage

        return return_data


# Last Run Timestamp per Platform
async def get_last_run_timestamp(platform: str):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = f"""
        SELECT end_time
        FROM processes
        WHERE status = 'success' AND platform = '{platform}'
        ORDER BY end_time DESC
        LIMIT 1
        """
        result = await session.execute(text(stmt))
        row = result.fetchone()
        return {
            "platform": platform,
            "last_successful_run": row.end_time if row else None,
        }


# Get all the process_id of a platform
async def get_all_platform_processes(platform: str) -> list[str]:
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        query = select(Processes.process_id).where(Processes.platform == platform)
        results = await session.execute(query)
        results = results.fetchall()
        return [process.process_id for process in results if process is not None]
