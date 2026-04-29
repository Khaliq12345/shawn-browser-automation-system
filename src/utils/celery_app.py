from celery import Celery
from celery.schedules import crontab
from src.config.config import REDIS_URL, SERVER_NAME, RUN_PER_BEAT_RUN
from src.utils.browser_runner import run_browser
from celery import group

app = Celery(SERVER_NAME, broker=REDIS_URL)

# Your existing settings
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True

# --- Crash & restart resilience ---
app.conf.worker_max_tasks_per_child = (
    200  # Restart worker process after N tasks (prevents memory leaks)
)
app.conf.worker_max_memory_per_child = (
    200_000  # Restart if worker exceeds 200MB (in KB)
)

# --- Connection resilience ---
app.conf.broker_connection_retry_on_startup = True
app.conf.broker_connection_retry = True
app.conf.broker_connection_max_retries = None  # Retry forever
app.conf.broker_transport_options = {
    "visibility_timeout": 3600,  # 1 hour — match your longest task
    "socket_keepalive": True,
    "retry_on_timeout": True,
}

# --- Task failure resilience ---
app.conf.task_reject_on_worker_lost = (
    True  # Re-queue tasks if worker dies mid-execution
)
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"

# --- Heartbeat & health ---
app.conf.broker_heartbeat = 10  # Detect dead broker connections faster
app.conf.broker_heartbeat_checkrate = 2


@app.task
def runner_parallel():
    """
    Runs multiple browser instances in parallel using Celery's group.
    """

    # Create a group of tasks to run in parallel
    RUN_PER_BEAT_RUN = 2
    job = group(run_browser_task.s() for _ in range(RUN_PER_BEAT_RUN))
    job.apply_async()

    return f"Launched {RUN_PER_BEAT_RUN} parallel browser tasks"


@app.task
def run_browser_task():
    """Individual browser task that can be run in parallel"""
    run_browser()
    return "SCRAPING DONE!"


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        crontab(minute="*/3"),
        runner_parallel.s(),
        name="BROWSER AUTOMATION",
    )
