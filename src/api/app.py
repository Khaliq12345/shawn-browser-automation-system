import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
from multiprocessing import Process
from fastapi.middleware.cors import CORSMiddleware
from src.utils.supabase import start_process, get_process_status
from src.platforms.gemini import GeminiScraper
from src.platforms.perplexity import PerplexityScraper
from src.platforms.chatgpt import ChatGPTScraper

app = FastAPI(title="Browser Automation System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    with ScraperClass(url=url, prompt=prompt, name=name, process_id=process_id) as browser:
        browser.send_prompt()

def run_browser_in_process(name: str, prompt: str, process_id: str):
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
    p = Process(target=run_browser, args=(name, prompt, process_id))
    p.start()
    # Save as running in supabase
    start_process(process_id, "running")
    return {"message": f"Browser started for {name}", "process_id": process_id}


@app.get("/check-status/{process_id}")
def check_status(process_id: str):
    # Get process status from supabase
    status = get_process_status(process_id)
    if status:
        return {"process_id": process_id, "status": status}
    raise HTTPException(status_code=404, detail="Process not found")
