from sqlmodel import select, text
from src.models.model import Processes, AWSUploads, get_engine
from datetime import datetime
from sqlalchemy.orm import sessionmaker


# Record an Upload on aws
def save_awsupload(
    aws_key: str,
    browser: str,
    prompt: str,
):
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    with Session() as session:
        item = AWSUploads(
            aws_key=aws_key,
            browser=browser,
            prompt=prompt,
            date=datetime.now(),
        )
        session.add(item)
        session.commit()
    engine.dispose()


# Record a starting process for any platform
def start_process(
    process_id: str,
    platform: str,
    prompt: str,
):
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    with Session() as session:
        item = Processes(
            process_id=process_id,
            status="running",
            platform=platform,
            prompt=prompt,
            start_time=datetime.now(),
            end_time=None,
        )
        session.add(item)
        session.commit()
    engine.dispose()


# Update the process status while running
def update_process_status(
    process_id: str,
    status: str,
):
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    with Session() as session:
        stmt = select(Processes).where(Processes.process_id == process_id)
        process = session.scalars(stmt)
        process = process.one()
        process.status = status
        process.end_time = datetime.now()
        process.duration = (
            (process.end_time - process.start_time).total_seconds()
            if process.end_time
            else 0.0
        )
        session.commit()
    engine.dispose()


# Retrieve a process status
def get_process_status(process_id: str):
    engine = get_engine()
    result = None
    Session = sessionmaker(bind=engine)
    with Session() as session:
        stmt = select(Processes).where(Processes.process_id == process_id)
        process = session.scalars(stmt)
        process = process.one()
        result = process.status
    engine.dispose()
    return result


#  -------- Metrics ----------


# Job Success Rate
def get_job_success_rate(start_date: datetime):
    engine = get_engine()
    session = sessionmaker(engine, expire_on_commit=False)
    combined_data = None
    with session() as session:
        stmt = f"""
        SELECT 
            COUNT(*) AS total_jobs,
            COALESCE(platform, 'all') AS platform,
            COUNT(CASE WHEN status = 'success' THEN 1 END) AS success_jobs,
            COALESCE(
                (COUNT(CASE WHEN status = 'success' THEN 1 END)::float / NULLIF(COUNT(*), 0)) * 100, 0
            ) AS success_rate
        FROM processes
        WHERE start_time > '{start_date}'
        GROUP BY ROLLUP(platform)
        """
        success_table = session.execute(text(stmt))
        keys = success_table.keys()
        values = success_table.fetchall()
        combined_data = [dict(zip(keys, row)) for row in values]
    engine.dispose()
    return combined_data


# Avg Job Duration
def get_average_job_duration(start_date: datetime):
    engine = get_engine()
    session = sessionmaker(engine, expire_on_commit=False)
    output = None
    with session() as session:
        stmt = f"""
        SELECT 
            COALESCE(platform, 'all') AS platform,
            COUNT(duration) AS total_jobs,
            COALESCE(AVG(duration), 0) AS average_duration_seconds
        FROM processes
        WHERE start_time >= '{start_date}'
        GROUP BY ROLLUP(platform)
        """
        success_table = session.execute(text(stmt))
        keys = success_table.keys()
        values = success_table.fetchall()
        output = [dict(zip(keys, row)) for row in values]
    engine.dispose()
    return output


# Avg Total Time per Prompt
def get_average_total_time_per_prompt(start_date: datetime):
    engine = get_engine()
    session = sessionmaker(engine, expire_on_commit=False)
    combined_data = None
    with session() as session:
        stmt = f"""
        SELECT 
            COUNT(duration) AS total_jobs,
            COALESCE(AVG(duration), 0) AS average_total_time_seconds,
            prompt as prompt
        FROM processes
        WHERE start_time >= '{start_date}'
        GROUP BY prompt
        """
        result = session.execute(text(stmt))
        keys = result.keys()
        values = result.fetchall()
        combined_data = [dict(zip(keys, row)) for row in values]
    engine.dispose()
    return combined_data


# Scraper Error Rate
def get_scraper_error_rate(start_date: datetime):
    engine = get_engine()
    session = sessionmaker(engine, expire_on_commit=False)
    outputs = None
    with session() as session:
        stmt = f"""
        SELECT 
            COALESCE(platform, 'all') as platform,
            COUNT(*) AS total_jobs,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) AS failed_jobs,
            COALESCE(
                (COUNT(CASE WHEN status = 'failed' THEN 1 END)::float / NULLIF(COUNT(*), 0)) * 100, 0
            ) AS failed_rate
        FROM processes
        WHERE start_time >= '{start_date}'
        GROUP BY ROLLUP(platform)
        """
        result = session.execute(text(stmt))
        keys = result.keys()
        values = result.fetchall()
        outputs = [dict(zip(keys, row)) for row in values]

    engine.dispose()
    return outputs


# Prompt Coverage Rate
def get_prompt_coverage_rate(start_date: datetime):
    engine = get_engine()
    session = sessionmaker(engine, expire_on_commit=False)
    outputs = None
    with session() as session:
        stmt = f"""
        SELECT 
            DISTINCT prompt as total
        FROM processes
        WHERE start_time >= '{start_date}'
        """
        result = session.execute(text(stmt))
        keys = result.keys()
        values = result.fetchall()
        outputs = [dict(zip(keys, row)) for row in values]

    engine.dispose()
    return outputs


# Last Run Timestamp per Platform
def get_last_run_timestamp(platform: str):
    engine = get_engine()
    output = None
    with sessionmaker(engine, expire_on_commit=False)() as session:
        # Use parameterized query to prevent SQL injection
        stmt = f"""
        SELECT * FROM public.processes
        WHERE platform = '{platform}'
        ORDER BY end_time DESC
        LIMIT 1
        """
        result = session.execute(text(stmt))
        keys = result.keys()
        values = result.first()
        if values:
            output = dict(zip(keys, values))

    engine.dispose()
    return output


# Get all the process_id of a platform
def get_all_platform_processes(platform: str) -> list[str]:
    engine = get_engine()
    session = sessionmaker(engine, expire_on_commit=False)
    outputs = None
    with session() as session:
        query = select(Processes.process_id).where(Processes.platform == platform)
        results = session.execute(query)
        results = results.fetchall()
        outputs = [process.process_id for process in results if process is not None]
    engine.dispose()
    return outputs


# Total Running Jobs
def get_total_running_jobs(start_date: datetime):
    engine = get_engine()
    session = sessionmaker(engine, expire_on_commit=False)
    outputs = None
    with session() as session:
        stmt = f"""
        SELECT 
            COALESCE(platform, 'all') as platform,
            COUNT(*) AS total_jobs,
            COUNT(CASE WHEN status = 'running' THEN 1 END) AS running_jobs,
            COALESCE(
                (COUNT(CASE WHEN status = 'running' THEN 1 END)::float / NULLIF(COUNT(*), 0)) * 100, 0
            ) AS running_rate
        FROM processes
        WHERE start_time >= '{start_date}'
        GROUP BY ROLLUP(platform)
        """
        result = session.execute(text(stmt))
        keys = result.keys()
        values = result.fetchall()
        outputs = [dict(zip(keys, row)) for row in values]

    engine.dispose()
    return outputs
