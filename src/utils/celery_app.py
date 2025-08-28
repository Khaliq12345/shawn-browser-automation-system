from celery import Celery
from playwright.sync_api import sync_playwright
from browserforge.fingerprints import Screen
from src.utils.globals import browser_dict

app = Celery(
    "tasks",
    broker="redis://localhost",
    backend="redis://localhost",
    include=["src.api.routes.globals"],
)


@app.task
def add(message: str):
    print(f"Your message is - {message}")
    return message


@app.task
def start_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    # browser = AsyncCamoufox(
    #     screen=Screen(max_width=1920, max_height=1080),
    #     headless=False,
    # )
    browser_dict["browser"] = browser
    print("Browser created")
    return "DONE"
