from src.platforms.google import GoogleScraper
from src.platforms.perplexity import PerplexityScraper
from src.platforms.chatgpt import ChatGPTScraper
from celery import Celery, signals
from camoufox.sync_api import Camoufox
import logging
from src.utils.redis_utils import RedisBase, RedisLogHandler
from src.config.config import REDIS_URL, HEADLESS


app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)


# Scrapper configs
SCRAPER_CONFIG = {
    "chatgpt": {"class": ChatGPTScraper, "url": "https://chatgpt.com/"},
    "google": {"class": GoogleScraper, "url": "https://google.com"},
    "perplexity": {
        "class": PerplexityScraper,
        "url": "https://www.perplexity.ai/",
    },
}

camoufox = None
browser = None


@signals.worker_process_init.connect
def init_worker(**kwargs):
    """Called once per worker process"""
    global camoufox, browser
    print("🔵 Starting browser for worker...")
    # logger.info("🔵 Starting Camoufox browser for worker...")
    camoufox = Camoufox(headless=HEADLESS == "true")
    browser = camoufox.start()


@signals.worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    """Called when worker process shuts down"""
    global camoufox, browser
    print("🔴 Closing browser for worker...")
    # logger.info("🔴 Closing Camoufox browser for worker...")
    if browser:
        browser.close()
    if camoufox:
        camoufox.stop()


@app.task
def run_browser(name: str, prompt: str, process_id: str, timeout: int, headless: bool):
    redis_handler = None
    global camoufox, browser
    # Redis log wrapper
    redis_logger = RedisBase(process_id)

    # Crée un logger spécifique pour cette tâche
    task_logger = logging.getLogger(f"{__name__}.{process_id}")
    task_logger.setLevel(logging.INFO)

    # Ajoute le handler Redis si pas déjà présent
    if not any(isinstance(h, RedisLogHandler) for h in task_logger.handlers):
        redis_handler = RedisLogHandler(redis_logger)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        redis_handler.setFormatter(formatter)
        task_logger.addHandler(redis_handler)

    task_logger.info("Getting matching class...")

    # Get the matching configs class and url
    config = SCRAPER_CONFIG[name]
    ScraperClass = config["class"]
    url = config["url"]

    # Launch the matching browser class
    if not browser:
        task_logger.error("Browser not created")
        print("Browser not created")
        # raise HTTPException(status_code=500, detail="Browser not created")

    matching_scraper = ScraperClass(
        browser=browser,
        logger=task_logger,
        url=url,
        prompt=prompt,
        name=name,
        process_id=process_id,
        timeout=timeout,
        headless=headless,
    )
    matching_scraper.send_prompt()
    if redis_handler:
        task_logger.removeHandler(redis_handler)


@app.task
def add(message: str):
    print(f"Your message is - {message}")
    return message
