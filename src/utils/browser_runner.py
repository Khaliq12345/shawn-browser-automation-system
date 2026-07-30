import asyncio
import logging
import sys
import threading

sys.path.append(".")
from datetime import datetime

from func_retry import retry
from src.config.config import MINUTES
from src.platforms.chatgpt import ChatGPTScraper
from src.platforms.google import GoogleScraper
from src.platforms.perplexity import PerplexityScraper
from src.utils.database import Database

# Scraper configs
SCRAPER_CONFIG = {
    "chatgpt": {"class": ChatGPTScraper, "url": "https://chatgpt.com/"},
    "google": {"class": GoogleScraper, "url": "https://www.google.com/"},
    "perplexity": {
        "class": PerplexityScraper,
        "url": "https://www.perplexity.ai/",
    },
}

PROCESS_TIMEOUT = 600  # 10 min max per attempt


def _run_scraper(scraper_class, scraper_kwargs, result):
    """
    Runs in an isolated thread with a brand new event loop.
    Playwright sync API requires no existing event loop in the current thread.
    """
    # Give this thread a clean event loop — critical for Playwright sync API
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        scraper = scraper_class(**scraper_kwargs)
        scraper.send_prompt()
        result["status"] = "success"
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        result["type"] = type(e).__name__
    finally:
        loop.close()


@retry(times=5, delay=60)
def _run_in_thread(ScraperClass, scraper_kwargs, task_logger):
    """
    Spawns a fresh thread for each attempt — isolates asyncio state
    from the Celery worker and from previous failed attempts.
    """
    result = {}
    t = threading.Thread(
        target=_run_scraper, args=(ScraperClass, scraper_kwargs, result)
    )
    t.start()
    t.join(timeout=PROCESS_TIMEOUT)

    if t.is_alive():
        task_logger.error(f"Thread timed out after {PROCESS_TIMEOUT}s")
        raise TimeoutError(f"send_prompt timed out after {PROCESS_TIMEOUT}s")

    if not result:
        raise RuntimeError("Thread exited without reporting a result")

    if result["status"] == "error":
        raise RuntimeError(f"{result['type']}: {result['message']}")


def test_runner():
    return "HEELO WORLD!"


def run_browser():
    database = Database()
    to_run = database.get_next_schedules()
    if not to_run:
        return None
    print(to_run)

    brand_report_id = to_run["brand_report_id"]
    report = database.get_report(brand_report_id)
    if not report:
        return None

    prompt = to_run["prompt"]
    prompt_id = to_run["prompt_id"]
    database.update_schedule(brand_report_id, prompt_id, prompt, minutes=MINUTES)
    date = datetime.now()

    for name in ["chatgpt", "google", "perplexity"]:
        config = SCRAPER_CONFIG[name]
        ScraperClass = config["class"]
        url = config["url"]

        country = report["country"]
        brand_report_id = report["brand_report_id"]
        timestamp = int(datetime.now().timestamp())
        process_id = f"{name}-{brand_report_id}-{prompt_id}-{timestamp}"
        brand = report["brand"]
        languague = report["languague"]

        # Logger for the parent process (subprocess gets its own)
        task_logger = logging.getLogger(f"{__name__}.{process_id}")
        task_logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        task_logger.addHandler(ch)
        task_logger.info("Getting matching class...")

        # Logger is not picklable — pass everything else, logger is recreated in subprocess
        scraper_kwargs = dict(
            logger=task_logger,  # logger is safe to share across threads
            url=url,
            prompt=prompt,
            name=name,
            process_id=process_id,
            timeout=60,
            country=country,
            brand_report_id=brand_report_id,
            prompt_id=prompt_id,
            date=date,
            brand=brand,
            languague=languague,
        )

        try:
            _run_in_thread(ScraperClass, scraper_kwargs, task_logger)
            task_logger.info(f"[{name}] Completed successfully")
        except Exception as e:
            task_logger.error(f"[{name}] All retries exhausted: {e}")


if __name__ == "__main__":
    run_browser()
