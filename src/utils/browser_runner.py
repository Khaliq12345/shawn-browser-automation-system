import logging
import multiprocessing
import sys

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


def _run_scraper(scraper_class, scraper_kwargs, result_queue):
    """
    Runs in a completely isolated subprocess — no shared asyncio loop,
    no shared memory with the parent Celery worker process.
    """
    # Set up a fresh logger inside the subprocess
    process_id = scraper_kwargs["process_id"]
    logger = logging.getLogger(process_id)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(ch)
    scraper_kwargs["logger"] = logger

    try:
        scraper = scraper_class(**scraper_kwargs)
        scraper.send_prompt()
        result_queue.put(("success", None))
    except Exception as e:
        result_queue.put(("error", e))


@retry(times=5, delay=2)
def _run_in_process(ScraperClass, scraper_kwargs, task_logger):
    """
    Spawns a fresh process for each attempt.
    Returns normally on success, raises on failure or timeout.
    """
    result_queue = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=_run_scraper,
        args=(ScraperClass, scraper_kwargs, result_queue),
    )
    p.start()
    p.join(timeout=PROCESS_TIMEOUT)

    if p.is_alive():
        task_logger.error(f"Process timed out after {PROCESS_TIMEOUT}s — terminating")
        p.terminate()
        p.join()
        raise TimeoutError(f"send_prompt timed out after {PROCESS_TIMEOUT}s")

    if result_queue.empty():
        raise RuntimeError("Process exited without reporting a result")

    status, error = result_queue.get()
    if status == "error":
        raise error


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
            logger=None,  # placeholder, replaced inside _run_scraper
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
            _run_in_process(ScraperClass, scraper_kwargs, task_logger)
            task_logger.info(f"[{name}] Completed successfully")
        except Exception as e:
            task_logger.error(f"[{name}] All retries exhausted: {e}")


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    run_browser()
