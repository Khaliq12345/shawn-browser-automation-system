from fastapi import APIRouter, HTTPException
import time
from src.utils.database import get_process_status, get_all_platform_processes
from src.platforms.google import GoogleScraper
from src.platforms.perplexity import PerplexityScraper
from src.platforms.chatgpt import ChatGPTScraper
from src.utils.celery_app import app


router = APIRouter(prefix="/globals")


# Scrapper configs
SCRAPER_CONFIG = {
    "chatgpt": {"class": ChatGPTScraper, "url": "https://chatgpt.com/"},
    "google": {"class": GoogleScraper, "url": "https://google.com"},
    "perplexity": {
        "class": PerplexityScraper,
        "url": "https://www.perplexity.ai/",
    },
}


@app.task
def run_browser(name: str, prompt: str, process_id: str, headless: bool):
    from src.utils.globals import browser_dict

    # Get the matching configs class and url
    config = SCRAPER_CONFIG[name]
    ScraperClass = config["class"]
    url = config["url"]
    print(config)

    # Launch the matching browser class
    if not browser_dict.get("browser"):
        raise HTTPException(status_code=500, detail="Browser not created")

    print(browser_dict)
    matching_scraper = ScraperClass(
        browser=browser_dict.get("browser"),
        url=url,
        prompt=prompt,
        name=name,
        process_id=process_id,
        headless=headless,
    )
    matching_scraper.send_prompt()


@router.post("/start-browser")
def start_browser(name: str, prompt: str, headless: bool = True):
    # If the name is not supported
    if name not in SCRAPER_CONFIG:
        raise HTTPException(status_code=400, detail="Invalid Parameter 'name'")
    timestamp = int(time.time())
    process_id = f"{name}_{timestamp}"
    # Start Process
    try:
        run_browser.apply_async(args=(name, prompt, process_id, headless))
    except Exception as e:
        print(f"errororr {e}")
        raise HTTPException(
            status_code=500, detail=f"Unable to create the process : {e}"
        )
    output = {
        "message": f"Browser started for {name}",
        "process_id": process_id,
    }
    return {"details": output}


@router.get("/check-status/{process_id}")
def check_status(process_id: str):
    try:
        # Get the process status
        status = get_process_status(process_id)
        if status:
            output = {"process_id": process_id, "status": status}
            return {"details": output}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Process not found : {e}")


@router.get("/get-processes/{platform}")
def get_processes(platform: str):
    try:
        outputs = get_all_platform_processes(platform)
        return {"details": outputs}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve processes for the platform : {e}",
        )
