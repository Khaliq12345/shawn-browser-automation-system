from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue
from src.config.config import REDIS_URL, SERVER_NAME, RUN_PER_BEAT_RUN
from src.utils.browser_runner import run_browser
from celery import group
import logging

logger = logging.getLogger(__name__)

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

# --Queue---
app.conf.task_create_missing_queues = True
app.conf.task_queues = (
    Queue("beat_triggers", Exchange("beat_triggers"), routing_key="beat_triggers"),
    Queue("new_jobs", Exchange("new_jobs"), routing_key="new_jobs"),
    Queue("scheduled_jobs", Exchange("scheduled_jobs"), routing_key="scheduled_jobs"),
)
app.conf.task_default_queue = "beat_triggers"


@app.task(queue="beat_triggers")
def runner_parallel():
    """
    Triggers every 3 mins via Beat. Dynamically routes browser tasks
    to different queues based on priority logic.
    """
    RUN_PER_BEAT_RUN = 2
    for i in range(RUN_PER_BEAT_RUN):
        # Dynamically assign the first run to high_priority, others to default
        if i == 0:
            target_queue = "new_jobs"
        else:
            target_queue = "scheduled_jobs"

        # Dispatch the task to the chosen queue dynamically
        run_browser_task.apply_async(queue=target_queue)
        logger.info(f"Added to {target_queue}")

    return f"Dispatched {RUN_PER_BEAT_RUN} tasks dynamically."


@app.task
def run_browser_task():
    """Single task definition handled by whichever queue it lands in"""
    run_browser()
    return "SCRAPING DONE!"


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        crontab(minute="*/3"),
        runner_parallel.s(),
        name="BROWSER AUTOMATION",
    )
