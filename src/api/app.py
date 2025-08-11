import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
from multiprocessing import Process
from fastapi.middleware.cors import CORSMiddleware
from src.models.model import create_db_and_tables
from src.utils.database import start_process, get_process_status
from src.platforms.gemini import GeminiScraper
from src.platforms.perplexity import PerplexityScraper
from src.platforms.chatgpt import ChatGPTScraper
from src.utils.redis_utils import get_redis_instance


app = FastAPI(title="Browser Automation System", on_startup=[create_db_and_tables])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scrapper configs
SCRAPER_CONFIG = {
    "chatgpt": {"class": ChatGPTScraper, "url": "https://chatgpt.com/"},
    "gemini": {"class": GeminiScraper, "url": "https://gemini.google.com"},
    "perplexity": {"class": PerplexityScraper, "url": "https://www.perplexity.ai/"},
}

def run_browser(name: str, prompt: str, process_id: str):
    # Get the matching configs class and url
    config = SCRAPER_CONFIG[name]
    ScraperClass = config["class"]
    url = config["url"]
    # Launch the matching browser class
    with ScraperClass(url=url, prompt=prompt, name=name, process_id=process_id) as browser:
        browser.send_prompt()

def run_browser_in_process(name: str, prompt: str, process_id: str):
    # Start a process for the platform
    p = Process(target=run_browser, args=(name, prompt, process_id))
    p.start()

@app.post("/start-browser")
def start_browser(name: str, prompt: str, background_tasks: BackgroundTasks):
    # If the name is not supported
    if name not in SCRAPER_CONFIG:
        raise HTTPException(status_code=404, detail="Invalid Parameter 'name'")
    timestamp = int(time.time())
    process_id = f"{name}_{timestamp}"
    # Start process in background
    background_tasks.add_task(run_browser_in_process, name, prompt, process_id)
    # Create and save in database as running
    start_process(process_id, "running", name, prompt)
    return {"message": f"Browser started for {name}", "process_id": process_id}


@app.get("/check-status/{process_id}")
def check_status(process_id: str):
    # Get the process status
    status = get_process_status(process_id)
    if status:
        return {"process_id": process_id, "status": status}
    raise HTTPException(status_code=404, detail="Process not found")


@app.get("/get-logs/{process_id}")
async def get_logs(process_id: str):
    # Extract platform name
    try:
        name, _ = process_id.split('_', 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid process_id format")
    # Get Matching Instance
    redis_class = get_redis_instance(name)
    if not redis_class:
        raise HTTPException(status_code=404, detail=f"No Redis instance for {name}")
    # Get Logs
    logs = await redis_class.get_log(process_id)
    return {"process_id": process_id, "logs": logs}