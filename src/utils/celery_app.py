from celery import Celery
<<<<<<< HEAD
from playwright.sync_api import sync_playwright
from browserforge.fingerprints import Screen
from src.utils.globals import browser_dict
=======
from camoufox.async_api import AsyncCamoufox
from browserforge.fingerprints import Screen
from src.utils import globals
>>>>>>> 05c1193 (Celery started)

app = Celery(
    "tasks",
    broker="redis://localhost",
    backend="redis://localhost",
    include=["src.api.routes.globals"],
)


@app.task
<<<<<<< HEAD
def add(message: str):
=======
async def add(message: str):
>>>>>>> 05c1193 (Celery started)
    print(f"Your message is - {message}")
    return message


@app.task
<<<<<<< HEAD
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
=======
async def create_browser():
    browser = AsyncCamoufox(
        screen=Screen(max_width=1920, max_height=1080),
        headless=True,
    )
    globals.browser = browser
    print("Browser Init")
    print(globals.browser)
    # return "Browser Set !"
>>>>>>> 05c1193 (Celery started)
