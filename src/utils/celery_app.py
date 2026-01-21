from celery import Celery
from celery.schedules import crontab
from src.config.config import REDIS_URL, SERVER_NAME, RUN_PER_BEAT_RUN
from src.utils.browser_runner import run_browser
from celery import group

app = Celery(SERVER_NAME, broker=REDIS_URL)


@app.task
def runner_parallel():
    """
    Runs multiple browser instances in parallel using Celery's group.
    """

    # Create a group of tasks to run in parallel
    job = group(run_browser_task.s() for _ in range(RUN_PER_BEAT_RUN))
    job.apply_async()

    return f"Launched {RUN_PER_BEAT_RUN} parallel browser tasks"


@app.task
def run_browser_task():
    """Individual browser task that can be run in parallel"""
    run_browser()
    print("SCRAPING STARTED")


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        crontab(minute="*/3"),
        runner_parallel.s(),
        name="BROWSER AUTOMATION",
    )
