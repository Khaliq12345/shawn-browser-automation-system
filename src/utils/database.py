from sqlmodel import select, text
from src.models.model import Processes, get_engine
from datetime import datetime
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
            start_time=datetime.now(),
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
        process = await session.scalars(stmt)
        process = process.one()
        process.status = status
        process.end_time = datetime.now()
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
        process = await session.scalars(stmt)
        process = process.one()
    await engine.dispose()
    return None


#  -------- Metrics ----------


# Job Success Rate
async def get_job_success_rate(start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    combined_data = None
    async with async_session() as session:
        stmt = f"""
        SELECT 
            COUNT(*) AS total_jobs,
            COALESCE(platform, 'all') AS platform,
            COUNT(CASE WHEN status = 'success' THEN 1 END) AS success_jobs,
            COALESCE(((COUNT(CASE WHEN status = 'success' THEN 1 END)::float / NULLIF(COUNT(*), 0)) * 100), 0) AS success_rate
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
async def get_average_job_duration(start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    output = None
    async with async_session() as session:
        stmt = f"""
        SELECT 
            COALESCE(platform, 'all') AS platform,
            COUNT(duration) AS total_jobs,
            COALESCE(AVG(duration), 0) AS average_duration_seconds
        FROM processes
        WHERE start_time >= '{start_date}'
        GROUP BY ROLLUP(platform)
        """
        success_table = await session.execute(text(stmt))
        keys = success_table.keys()
        values = success_table.fetchall()
        output = [dict(zip(keys, row)) for row in values]
    await engine.dispose()
    return output


# Avg Total Time per Prompt
async def get_average_total_time_per_prompt(start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    combined_data = None
    async with async_session() as session:
        stmt = f"""
        SELECT 
            COUNT(duration) AS total_jobs,
            COALESCE(AVG(duration), 0) AS average_total_time_seconds,
            prompt as prompt
        FROM processes
        WHERE start_time >= '{start_date}'
        GROUP BY prompt
        """
        result = await session.execute(text(stmt))
        keys = result.keys()
        values = result.fetchall()
        combined_data = [dict(zip(keys, row)) for row in values]
    await engine.dispose()
    return combined_data


# Scraper Error Rate
async def get_scraper_error_rate(start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    outputs = None
    async with async_session() as session:
        stmt = f"""
        SELECT 
            COALESCE(platform, 'all') as platform,
            COUNT(*) AS total_jobs,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) AS failed_jobs,
            COALESCE(((COUNT(CASE WHEN status = 'failed' THEN 1 END)::float / NULLIF(COUNT(*), 0)) * 100), 0) as failed_rate
        FROM processes
        WHERE start_time >= '{start_date}'
        GROUP BY ROLLUP(platform)
        """
        result = await session.execute(text(stmt))
        keys = result.keys()
        values = result.fetchall()
        outputs = [dict(zip(keys, row)) for row in values]

    await engine.dispose()
    return outputs


# Prompt Coverage Rate
async def get_prompt_coverage_rate(start_date: datetime):
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    outputs = None
    async with async_session() as session:
        stmt = f"""
        SELECT 
            DISTINCT prompt as total
        FROM processes
        WHERE start_time >= '{start_date}'
        """
        result = await session.execute(text(stmt))
        keys = result.keys()
        values = result.fetchall()
        outputs = [dict(zip(keys, row)) for row in values]

    await engine.dispose()
    return outputs


# Last Run Timestamp per Platform
async def get_last_run_timestamp(platform: str):
    engine = get_engine()
    output = None
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        # Use parameterized query to prevent SQL injection
        stmt = f"""
        SELECT * FROM public.processes
        WHERE platform = '{platform}'
        ORDER BY end_time DESC
        LIMIT 1
        """
        result = await session.execute(text(stmt))
        keys = result.keys()
        values = result.first()
        if values:
            output = dict(zip(keys, values))

    await engine.dispose()
    return output


# Get all the process_id of a platform
async def get_all_platform_processes(platform: str) -> list[str]:
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    outputs = None
    async with async_session() as session:
        query = select(Processes.process_id).where(
            Processes.platform == platform
        )
        results = await session.execute(query)
        results = results.fetchall()
        outputs = [
            process.process_id for process in results if process is not None
        ]
    await engine.dispose()
    return outputs
