from src.platforms.google import GoogleScraper
from src.platforms.perplexity import PerplexityScraper
from src.platforms.chatgpt import ChatGPTScraper
from celery import Celery, signals
from playwright.sync_api import sync_playwright

app = Celery(
    "tasks",
    broker="redis://localhost",
    backend="redis://localhost",
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

playwright = None
browser = None


@signals.worker_process_init.connect
def init_worker(**kwargs):
    """Called once per worker process"""
    global playwright, browser
    print("🔵 Starting browser for worker...")

    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=False)


@signals.worker_shutdown.connect
def shutdown_worker(**kwargs):
    """Called when worker process shuts down"""
    global playwright, browser
    print("🔴 Closing browser for worker...")

    if browser:
        browser.close()
    if playwright:
        playwright.stop()


@app.task
def run_browser(name: str, prompt: str, process_id: str, headless: bool):
    global playwright, browser
    # Get the matching configs class and url
    config = SCRAPER_CONFIG[name]
    ScraperClass = config["class"]
    url = config["url"]

    # Launch the matching browser class
    if not browser:
        print("Browser not created")
        # raise HTTPException(status_code=500, detail="Browser not created")

    matching_scraper = ScraperClass(
        browser=browser,
        url=url,
        prompt=prompt,
        name=name,
        process_id=process_id,
        headless=headless,
    )
    matching_scraper.send_prompt()


@app.task
def add(message: str):
    print(f"Your message is - {message}")
    return message

