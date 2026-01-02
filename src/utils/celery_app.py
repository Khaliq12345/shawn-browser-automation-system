from celery import Celery
from celery.schedules import crontab
from src.config.config import REDIS_URL, SERVER_NAME, RUN_PER_BEAT_RUN
from src.utils.browser_runner import run_browser  

app = Celery(SERVER_NAME, broker=REDIS_URL)

@app.task
def runner():
    return run_browser()

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    for idx in range(RUN_PER_BEAT_RUN):
        sender.add_periodic_task(
            crontab(minute="*/3"),
            runner.s(),
            name=f"BROWSER AUTOMATION: {idx+1}",
        ) 
