from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.models.model import create_db_and_tables
from src.api.routes.metrics import router as metrics_router
from src.api.routes.globals import router as global_router


app = FastAPI(
    title="Browser Automation System", on_startup=[create_db_and_tables]
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
app.include_router(prefix="/api", router=global_router, tags=["Globals"])
