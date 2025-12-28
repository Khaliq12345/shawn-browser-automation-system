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
    for i in range(2): # send it in the env
        schedule_num = i + 1
        sender.add_periodic_task(
            crontab(minute="*/3"),
            runner.s(),
            name=f"BROWSER AUTOMATION #{schedule_num}",
        ) 
