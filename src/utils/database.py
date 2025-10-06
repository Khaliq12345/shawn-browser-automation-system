import sys

sys.path.append(".")

from sqlmodel import Session, select, text, create_engine
from src.models.model import Browsers, Reports, SQLModel, Schedules
from datetime import datetime
from src.config import config
from dateparser import parse


class Database:
    def __init__(self) -> None:
        self.engine = create_engine(
            f"postgresql+psycopg://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:5432/{config.DB_NAME}"
        )

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)

    #  -------- Schedules ----------
    def update_schedule(self, brand_report_id: str, prompt_id: str, prompt: str):
        """Update or create the schedule"""
        print("Updating or Adding schedule")
        with Session(self.engine) as session:
            stmt = select(Schedules).where(
                Schedules.brand_report_id == brand_report_id,
                Schedules.prompt_id == prompt_id,
            )
            schedule = session.exec(stmt).first()
            # update the schedule if it exists
            if schedule:
                schedule.last_run = datetime.now()
                schedule.next_run = parse("In 24 hours")
            # creating a new one
            else:
                schedule = Schedules(
                    prompt_id=prompt_id,
                    brand_report_id=brand_report_id,
                    prompt=prompt,
                    last_run=datetime.now(),
                    next_run=parse("In 24 hours"),
                )
            session.add(schedule)
            session.commit()

    #  -------- Reports ----------

    def add_report(
        self,
        brand_report_id: str,
        languague: str,
        country: str,
        brand: str,
        domain: str,
        date: datetime,
    ):
        """Add new report"""
        print("Adding new report")
        with Session(self.engine) as session:
            stmt = select(Reports).where(Reports.brand_report_id == brand_report_id)
            item = session.exec(stmt).first()
            if item:
                print("Report existed already")
                return None
            item = Reports(
                brand_report_id=brand_report_id,
                languague=languague,
                country=country,
                brand=brand,
                domain=domain,
                date=date,
            )
            session.add(item)
            session.commit()

    #  -------- Process ----------

    def start_process(
        self, process_id: str, platform: str, prompt: str, brand_report_id: str
    ):
        with Session(self.engine) as session:
            item = Browsers(
                process_id=process_id,
                status="running",
                platform=platform,
                prompt=prompt,
                start_time=datetime.now(),
                end_time=None,
                brand_report_id=brand_report_id,
            )
            session.add(item)
            session.commit()

    def update_process_status(
        self,
        process_id: str,
        status: str,
    ):
        with Session(self.engine) as session:
            stmt = select(Browsers).where(Browsers.process_id == process_id)
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

    # Retrieve a process status
    def get_process_status(self, process_id: str):
        result = None
        with Session(self.engine) as session:
            stmt = select(Browsers).where(Browsers.process_id == process_id)
            process = session.scalars(stmt)
            process = process.one()
            result = process.status
        return result

    #  -------- Metrics ----------

    # Job Success Rate
    def get_job_success_rate(self, start_date: datetime):
        combined_data = None
        with Session(self.engine) as session:
            stmt = f"""
            SELECT 
                COUNT(*) AS total_jobs,
                COALESCE(platform, 'all') AS platform,
                COUNT(CASE WHEN status = 'success' THEN 1 END) AS success_jobs,
                COALESCE(
                    (COUNT(CASE WHEN status = 'success' THEN 1 END)::float / NULLIF(COUNT(*), 0)) * 100, 0
                ) AS success_rate
            FROM browser
            WHERE start_time > '{start_date}'
            GROUP BY ROLLUP(platform)
            """
            success_table = session.execute(text(stmt))
            keys = success_table.keys()
            values = success_table.fetchall()
            combined_data = [dict(zip(keys, row)) for row in values]
        return combined_data

    # Avg Job Duration
    def get_average_job_duration(self, start_date: datetime):
        output = None
        with Session(self.engine) as session:
            stmt = f"""
            SELECT 
                COALESCE(platform, 'all') AS platform,
                COUNT(duration) AS total_jobs,
                COALESCE(AVG(duration), 0) AS average_duration_seconds
            FROM browser
            WHERE start_time >= '{start_date}'
            GROUP BY ROLLUP(platform)
            """
            success_table = session.execute(text(stmt))
            keys = success_table.keys()
            values = success_table.fetchall()
            output = [dict(zip(keys, row)) for row in values]
        return output

    # Avg Total Time per Prompt
    def get_average_total_time_per_prompt(self, start_date: datetime):
        combined_data = None
        with Session(self.engine) as session:
            stmt = f"""
            SELECT 
                COUNT(duration) AS total_jobs,
                COALESCE(AVG(duration), 0) AS average_total_time_seconds,
                prompt as prompt
            FROM browser
            WHERE start_time >= '{start_date}'
            GROUP BY prompt
            """
            result = session.execute(text(stmt))
            keys = result.keys()
            values = result.fetchall()
            combined_data = [dict(zip(keys, row)) for row in values]
        return combined_data

    # Scraper Error Rate
    def get_scraper_error_rate(self, start_date: datetime):
        outputs = None
        with Session(self.engine) as session:
            stmt = f"""
            SELECT 
                COALESCE(platform, 'all') as platform,
                COUNT(*) AS total_jobs,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) AS failed_jobs,
                COALESCE(
                    (COUNT(CASE WHEN status = 'failed' THEN 1 END)::float / NULLIF(COUNT(*), 0)) * 100, 0
                ) AS failed_rate
            FROM browser
            WHERE start_time >= '{start_date}'
            GROUP BY ROLLUP(platform)
            """
            result = session.execute(text(stmt))
            keys = result.keys()
            values = result.fetchall()
            outputs = [dict(zip(keys, row)) for row in values]

        return outputs

    # Prompt Coverage Rate
    def get_prompt_coverage_rate(self, start_date: datetime):
        outputs = None
        with Session(self.engine) as session:
            stmt = f"""
            SELECT 
                DISTINCT prompt as total
            FROM browser
            WHERE start_time >= '{start_date}'
            """
            result = session.execute(text(stmt))
            keys = result.keys()
            values = result.fetchall()
            outputs = [dict(zip(keys, row)) for row in values]

        return outputs

    # Last Run Timestamp per Platform
    def get_last_run_timestamp(self, platform: str):
        output = None
        with Session(self.engine) as session:
            # Use parameterized query to prevent SQL injection
            stmt = f"""
            SELECT * FROM public.browser
            WHERE platform = '{platform}'
            ORDER BY end_time DESC
            LIMIT 1
            """
            result = session.execute(text(stmt))
            keys = result.keys()
            values = result.first()
            if values:
                output = dict(zip(keys, values))

        return output

    # Get all the process_id of a platform
    def get_all_platform_processes(self, platform: str) -> list[str]:
        outputs = None
        with Session(self.engine) as session:
            query = select(Browsers.process_id).where(Browsers.platform == platform)
            results = session.execute(query)
            results = results.fetchall()
            outputs = [process.process_id for process in results if process is not None]
        return outputs

    # Total Running Jobs
    def get_total_running_jobs(self, start_date: datetime):
        outputs = None
        with Session(self.engine) as session:
            stmt = f"""
            SELECT 
                COALESCE(platform, 'all') as platform,
                COUNT(*) AS total_jobs,
                COUNT(CASE WHEN status = 'running' THEN 1 END) AS running_jobs,
                COALESCE(
                    (COUNT(CASE WHEN status = 'running' THEN 1 END)::float / NULLIF(COUNT(*), 0)) * 100, 0
                ) AS running_rate
            FROM browser
            WHERE start_time >= '{start_date}'
            GROUP BY ROLLUP(platform)
            """
            result = session.execute(text(stmt))
            keys = result.keys()
            values = result.fetchall()
            outputs = [dict(zip(keys, row)) for row in values]

        return outputs


if __name__ == "__main__":
    database = Database()
    database.create_db_and_tables()
