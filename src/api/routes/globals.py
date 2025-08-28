import asyncio
from fastapi import APIRouter, HTTPException
import time
from src.utils.database import get_process_status, get_all_platform_processes
from src.platforms.google import GoogleScraper
from src.platforms.perplexity import PerplexityScraper
from src.platforms.chatgpt import ChatGPTScraper
from multiprocessing import Process
import task


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


def run_browser(name: str, prompt: str, process_id: str, headless: bool):
    # Get the matching configs class and url
    config = SCRAPER_CONFIG[name]
    ScraperClass = config["class"]
    url = config["url"]
    # Launch the matching browser class
    matching_scraper = ScraperClass(
        url=url,
        prompt=prompt,
        name=name,
        process_id=process_id,
        headless=headless,
    )
    asyncio.run(matching_scraper.send_prompt())


@router.post("/start-browser")
async def start_browser(name: str, prompt: str, headless: bool = True):
    # If the name is not supported
    if name not in SCRAPER_CONFIG:
        raise HTTPException(status_code=400, detail="Invalid Parameter 'name'")
    timestamp = int(time.time())
    process_id = f"{name}_{timestamp}"
    # Start Process
    try:
        p = Process(target=run_browser, args=(name, prompt, process_id, headless))
        p.start()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to create the process : {e}"
        )
    output = {
        "message": f"Browser started for {name}",
        "process_id": process_id,
    }
    return {"details": output}


@router.get("/check-status/{process_id}")
async def check_status(process_id: str):
    try:
        # Get the process status
        status = await get_process_status(process_id)
        if status:
            output = {"process_id": process_id, "status": status}
            return {"details": output}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Process not found : {e}")


@router.get("/get-processes/{platform}")
async def get_processes(platform: str):
    try:
        outputs = await get_all_platform_processes(platform)
        return {"details": outputs}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve processes for the platform : {e}",
        )


@router.get("/test-celery")
async def send_message(message: str):
    result = task.add.apply_async(args=(message,))
    print(result)
    print(result.get())


@router.get("/get-celery")
async def get_message(message: str):
    task.add
