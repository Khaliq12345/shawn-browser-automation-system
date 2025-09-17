import time
from fastapi import FastAPI, HTTPException, Path, Security, Depends, Query
from fastapi.security.api_key import APIKeyQuery
from fastapi.middleware.cors import CORSMiddleware
from src.models.model import (
    CheckStatusResponse,
    GetProcessesResponse,
    StartBrowserResponse,
    create_db_and_tables,
)
from src.api.routes.metrics import router as metrics_router
from src.api.routes.logs import router as logs_router
from src.utils.database import get_process_status, get_all_platform_processes
from src.utils import celery_app
from contextlib import asynccontextmanager
from src.config.config import API_KEY

API_KEY_NAME = "api_key"
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key_query: str = Security(api_key_query)):
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
    description="""
    Cette API permet d'automatiser des navigateurs pour exécuter des scrapers, 
    récupérer des métriques de performance, et gérer les processus en cours.
    
    Chaque endpoint est sécurisé via une clé API fournie dans les query params.
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Metrics",
            "description": "Endpoints pour récupérer les métriques des jobs, taux de réussite, durée moyenne, erreurs, etc.",
        },
        {
            "name": "Logs",
            "description": "Endpoints pour récupérer les logs des processus.",
        },
    ],
    responses={
        400: {"description": "Bad Request"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
    lifespan=lifespan,
    dependencies=[Depends(get_api_key)],
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


@app.post(
    "/api/globals/start-browser",
    response_model=StartBrowserResponse,
    summary="Start Browser",
    description="""
        Démarre un processus de navigateur pour un scraper donné.

        - **name** : nom du scraper à utiliser (doit être dans la configuration)
        - **prompt** : prompt ou tâche à exécuter
        - **country** : code du pays pour le scraper
        - **timeout** : durée maximale (en ms) avant l’arrêt du processus
        """,
    responses={
        200: {
            "description": "Browser successfully started",
            "content": {
                "application/json": {
                    "example": {
                        "details": {
                            "message": "Browser started for google",
                            "process_id": "google_1694948567",
                        }
                    }
                }
            },
        },
        400: {"description": "Invalid Parameter"},
        500: {"description": "Server Error"},
        422: {"description": "Validation Error"},
    },
)
def start_browser(
    name: str = Query(..., description="Nom du scraper à utiliser", example="google"),
    prompt: str = Query(
        ..., description="Prompt ou tâche à exécuter", example="Scrape latest news"
    ),
    country: str = Query(..., description="Code du pays pour le scraper", example="FR"),
    timeout: int = Query(240000, description="Timeout en ms", example=240000),
):
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


@app.get(
    "/api/globals/check-status/{process_id}",
    response_model=CheckStatusResponse,
    summary="Check Process Status",
    description="""
Récupère le statut d’un processus de navigateur.

- **process_id** : identifiant du processus à vérifier.
- La réponse contient `status` qui peut être `running`, `completed` ou `failed`.
""",
    responses={
        200: {
            "description": "Process status retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "details": {
                            "process_id": "chrome_1694948567",
                            "status": "running",
                        }
                    }
                }
            },
        },
        404: {"description": "Process not found"},
        422: {"description": "Validation Error"},
    },
)
def check_status(
    process_id: str = Path(
        ..., description="Identifiant du processus", example="google_1694948567"
    ),
):
    try:
        # Get the process status
        status = get_process_status(process_id)
        if status:
            output = {"process_id": process_id, "status": status}
            return {"details": output}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Process not found : {e}")


@app.get(
    "/api/globals/get-processes/{platform}",
    response_model=GetProcessesResponse,
    summary="Get Processes for Platform",
    description="""
Récupère tous les processus d’un scraper pour une plateforme donnée.

- **platform** : nom de la plateforme.
- La réponse contient une liste de processus avec leur ID, nom, pays et statut.
""",
    responses={
        200: {
            "description": "Processes retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "details": [
                            {
                                "process_id": "google_1694948567",
                                "status": "running",
                                "name": "google",
                                "country": "FR",
                            },
                            {
                                "process_id": "fchatgpt_1694948600",
                                "status": "completed",
                                "name": "chatgpt",
                                "country": "US",
                            },
                        ]
                    }
                }
            },
        },
        500: {"description": "Unable to retrieve processes"},
        422: {"description": "Validation Error"},
    },
)
def get_processes(
    platform: str = Path(..., description="Nom de la plateforme", example="google"),
):
    try:
        outputs = get_all_platform_processes(platform)
        return {"details": outputs}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve processes for the platform : {e}",
        )
