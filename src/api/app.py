from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.models.model import create_db_and_tables
from contextlib import asynccontextmanager
from src.api.routes.metrics import router as metrics_router
from src.api.routes.globals import router as global_router
from src.api.routes.logs import router as logs_router
from src.utils.celery_app import create_browser


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage de l'app
    await create_db_and_tables()
    await create_browser()

    yield


app = FastAPI(
    title="Browser Automation System",
    # on_startup=[create_db_and_tables, create_browser],
    lifespan=lifespan,
    responses={
        400: {"description": "Bad Request"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
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
app.include_router(prefix="/api", router=logs_router, tags=["Logs"])
