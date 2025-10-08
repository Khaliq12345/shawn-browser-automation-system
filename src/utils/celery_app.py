from src.platforms.google import GoogleScraper
from src.platforms.perplexity import PerplexityScraper
from src.platforms.chatgpt import ChatGPTScraper
from celery import Celery
import logging
from src.utils.redis_utils import RedisBase, RedisLogHandler
from src.config.config import REDIS_URL


app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)


# Scrapper configs
SCRAPER_CONFIG = {
    "chatgpt": {"class": ChatGPTScraper, "url": "https://chatgpt.com/"},
    "google": {"class": GoogleScraper, "url": "https://www.google.com/"},
    "perplexity": {
        "class": PerplexityScraper,
        "url": "https://www.perplexity.ai/",
    },
}


@app.task
def run_browser(
    name: str,
    prompt: str,
    process_id: str,
    timeout: int,
    country: str,
    brand_report_id: str,
    languague: str,
    date: str,
):
    redis_handler = None
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

    matching_scraper = ScraperClass(
        logger=task_logger,
        url=url,
        prompt=prompt,
        name=name,
        process_id=process_id,
        timeout=timeout,
        country=country,
        brand_report_id=brand_report_id,
        date=date,
    )
    matching_scraper.send_prompt()
    if redis_handler:
        task_logger.removeHandler(redis_handler)
