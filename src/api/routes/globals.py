from fastapi import APIRouter, HTTPException
import time
from src.utils.database import get_process_status
from platforms.google import GoogleScraper
from src.platforms.perplexity import PerplexityScraper
from src.platforms.chatgpt import ChatGPTScraper
from src.utils.redis_utils import RedisBase
from multiprocessing import Process


router = APIRouter(prefix="/globals")


# Scrapper configs
SCRAPER_CONFIG = {
    "chatgpt": {"class": ChatGPTScraper, "url": "https://chatgpt.com/"},
    "gemini": {"class": GoogleScraper, "url": "https://gemini.google.com"},
    "perplexity": {
        "class": PerplexityScraper,
        "url": "https://www.perplexity.ai/",
    },
}


def run_browser(name: str, prompt: str, process_id: str):
    # Get the matching configs class and url
    config = SCRAPER_CONFIG[name]
    ScraperClass = config["class"]
    url = config["url"]
    # Launch the matching browser class
    gemini_scraper = ScraperClass(
        url=url, prompt=prompt, name=name, process_id=process_id
    )
    gemini_scraper.run_browser()


@router.post("/start-browser")
async def start_browser(name: str, prompt: str):
    # If the name is not supported
    if name not in SCRAPER_CONFIG:
        raise HTTPException(status_code=404, detail="Invalid Parameter 'name'")
    timestamp = int(time.time())
    process_id = f"{name}_{timestamp}"
    # Start Process
    p = Process(target=run_browser, args=(name, prompt, process_id))
    p.start()
    return {"message": f"Browser started for {name}", "process_id": process_id}


@router.get("/check-status/{process_id}")
def check_status(process_id: str):
    # Get the process status
    status = get_process_status(process_id)
    if status:
        return {"process_id": process_id, "status": status}
    raise HTTPException(status_code=404, detail="Process not found")


@router.get("/get-logs/{process_id}")
def get_logs(process_id: str):
    # Get Matching Instance
    redis_base = RedisBase(process_id)
    # Get Logs
    logs = redis_base.get_log()
    return {"process_id": process_id, "logs": logs}
