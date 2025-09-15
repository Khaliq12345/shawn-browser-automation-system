import time
from fastapi import FastAPI, HTTPException,Security,Depends
from fastapi.security.api_key import APIKeyQuery
from fastapi.middleware.cors import CORSMiddleware
from src.models.model import create_db_and_tables
from src.api.routes.metrics import router as metrics_router
from src.api.routes.logs import router as logs_router
from src.utils.database import get_process_status, get_all_platform_processes
from src.utils import celery_app
from contextlib import asynccontextmanager
from src.config.config import API_KEY

API_KEY_NAME = "api_key"
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_query: str = Security(api_key_query)):
    if api_key_query == API_KEY:
        print("Autorisation réussi")
        return api_key_query
    raise HTTPException(status_code=403, detail="Invalid or missing API Key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Browser Automation System",
    responses={
        400: {"description": "Bad Request"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(prefix="/api", router=metrics_router, tags=["Metrics"])
app.include_router(prefix="/api", router=logs_router, tags=["Logs"])


@app.post("/api/globals/start-browser")
def start_browser(name: str, prompt: str, country: str, timeout: int = 240000,api_key:str=Depends(get_api_key)):
    # If the name is not supported
    if name not in celery_app.SCRAPER_CONFIG:
        raise HTTPException(status_code=400, detail="Invalid Parameter 'name'")
    timestamp = int(time.time())
    process_id = f"{name}_{timestamp}"
    # Start Process
    try:
        celery_app.run_browser.apply_async(
            args=(name, prompt, process_id, timeout, country)
        )
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


@app.get("/api/globals/check-status/{process_id}")
def check_status(process_id: str):
    try:
        # Get the process status
        status = get_process_status(process_id)
        if status:
            output = {"process_id": process_id, "status": status}
            return {"details": output}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Process not found : {e}")


@app.get("/api/globals/get-processes/{platform}")
def get_processes(platform: str):
    try:
        outputs = get_all_platform_processes(platform)
        return {"details": outputs}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve processes for the platform : {e}",
        )
