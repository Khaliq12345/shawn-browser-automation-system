from celery import Celery
from celery.schedules import crontab
from src.config.config import REDIS_URL, SERVER_NAME
from src.utils.browser_runner import run_browser  

app = Celery(SERVER_NAME, broker=REDIS_URL)

@app.task
def runner():
    return run_browser()

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        crontab(minute="*/3"),
        runner.s(),
        name="BROWSER AUTOMATION"
    )
