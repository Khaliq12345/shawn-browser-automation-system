from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.metrics import router as metrics_router
from src.api.routes.logs import router as logs_router
from src.api.routes.browser import router as browser_router
from src.api.routes.schedule import router as schedule_router
from src.utils.database import Database
from src.config.config import API_KEY

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid or missing API Key")


app = FastAPI(
    title="Browser Automation System",
    responses={
        400: {"description": "Bad Request"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
    dependencies=[Depends(get_api_key)],
    on_startup=[Database().create_db_and_tables],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(prefix="/api", router=browser_router, tags=["Browser"])
app.include_router(prefix="/api", router=schedule_router, tags=["Schedule"])
app.include_router(prefix="/api", router=metrics_router, tags=["Metrics"])
app.include_router(prefix="/api", router=logs_router, tags=["Logs"])
