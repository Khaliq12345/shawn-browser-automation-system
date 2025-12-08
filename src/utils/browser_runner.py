import sys

sys.path.append(".")

from datetime import datetime
import logging
import textwrap
from typing import Any

from src.platforms.google import GoogleScraper
from src.platforms.perplexity import PerplexityScraper
from src.utils.slack_service import SlackBase

from src.platforms.chatgpt import ChatGPTScraper
from src.utils.database import Database

from src.config.config import MINUTES

# Scrapper configs
SCRAPER_CONFIG = {
    "chatgpt": {"class": ChatGPTScraper, "url": "https://chatgpt.com/"},
    "google": {"class": GoogleScraper, "url": "https://www.google.com/"},
    "perplexity": {
        "class": PerplexityScraper,
        "url": "https://www.perplexity.ai/",
    },
}


def error_handler(exc: Any, name: str, brand: str, country: str, languague: str, brand_report_id: str, prompt_id: str, process_id: str, prompt: str):
    # Send Slack notification on final failure
    slack = SlackBase()
    # Message with all task details
    error_message = textwrap.dedent(f"""
        *Date/Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        *Task Details:*
        • Platform: `{name}`
        • Brand: `{brand}`
        • Country: `{country}`
        • Language: `{languague}`
        • Brand Report ID: `{brand_report_id}`
        • Prompt ID: `{prompt_id}`
        • Process ID: `{process_id}`

        *Prompt:*
        ```
        {prompt}
        ```

        *Error:*
        ```
        {str(exc)}
        ```
    """).strip()
    # slack.send_message(error_message)


def run_browser():
    database = Database()
    schedules = database.get_next_schedules()
    if not schedules:
        return None

    to_run = schedules[0]
    print(to_run)
    brand_report_id = to_run["brand_report_id"]
    report = database.get_report(brand_report_id)
    if not report:
        return None
    prompt = to_run["prompt"]
    prompt_id = to_run["prompt_id"]

    database.update_schedule(brand_report_id, prompt_id, prompt, minutes=MINUTES)
    # start the scraper 
    for name in ["chatgpt", "google", "perplexity"]:
        # Get the matching configs class and url
        config = SCRAPER_CONFIG[name]
        ScraperClass = config["class"]
        url = config["url"]
        timeout = 60
        country = report["country"]
        brand_report_id = report["brand_report_id"]
        timestamp = int(datetime.now().timestamp())
        process_id = f"{name}-{brand_report_id}-{prompt_id}-{timestamp}"
        date = report["date"]
        brand = report["brand"]
        languague = report["languague"]

        #setup a logger
        task_logger = logging.getLogger(f"{__name__}.{process_id}")
        task_logger.setLevel(logging.INFO)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        task_logger.addHandler(ch)

        task_logger.info("Getting matching class...")

        try:
            matching_scraper = ScraperClass(
            logger=task_logger,
            url=url,
            prompt=prompt,
            name=name,
            process_id=process_id,
            timeout=timeout,
            country=country,
            brand_report_id=brand_report_id,
            prompt_id=prompt_id,
            date=date,
            brand=brand,
            languague=languague,
        )
            matching_scraper.send_prompt()
        except Exception as e:
            task_logger.exception(f"run_browser failed, will retry - {str(e)}")


if __name__ == "__main__":
    run_browser()
