from celery import Celery
from camoufox.async_api import AsyncCamoufox
from browserforge.fingerprints import Screen
from src.utils import globals

app = Celery(
    "tasks",
    broker="redis://localhost",
    backend="redis://localhost",
    include=["src.api.routes.globals"],
)


@app.task
async def add(message: str):
    print(f"Your message is - {message}")
    return message


@app.task
async def create_browser():
    browser = AsyncCamoufox(
        screen=Screen(max_width=1920, max_height=1080),
        headless=True,
    )
    globals.browser = browser
    print("Browser Init")
    print(globals.browser)
    # return "Browser Set !"
