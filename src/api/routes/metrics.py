import dateparser
from fastapi import APIRouter, HTTPException, Query
from enum import Enum
from src.models.model import (
    AverageJobDurationResponse,
    AverageTotalTimePerPromptResponse,
    JobSuccessRateResponse,
    LastRunTimestampResponse,
    PromptCoverageRateResponse,
    ScraperErrorRateResponse,
    TotalRunningJobsResponse,
)
from src.utils.database import (
    get_job_success_rate,
    get_average_job_duration,
    get_average_total_time_per_prompt,
    get_scraper_error_rate,
    get_prompt_coverage_rate,
    get_last_run_timestamp,
    get_total_running_jobs,
)


router = APIRouter(prefix="/metrics")


class DateOptions(str, Enum):
    hours_24 = "24 hours ago"
    one_week = "1 week ago"
    one_month = "1 month ago"
    one_year = "1 year ago"


# Job Success Rate
@router.get(
    "/job-success-rate",
    response_model=JobSuccessRateResponse,
    summary="Job Success Rate",
    description="""
Récupère le taux de succès des jobs pour une plateforme donnée.

- **date** : période à analyser (ex: "24 hours ago", "1 week ago", etc.)
- **platform** : nom de la plateforme
- La réponse contient `success_rate` 
""",
    responses={
        200: {
            "description": "Success rate retrieved successfully",
            "content": {
                "application/json": {
                    "example": {"details": {"platform": "google", "success_rate": 0.92}}
                }
            },
        },
        400: {"description": "Invalid date"},
        500: {"description": "Unable to execute the request"},
        422: {"description": "Validation Error"},
    },
)
def job_success_rate(
    date: DateOptions = Query(
        ..., description="Période à analyser", example="24 hours ago"
    ),
    platform: str = Query(..., description="Nom de la plateforme", example="google"),
):
    # Validation
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = get_job_success_rate(parsed_date)
        for output in outputs:
            if output["platform"] == platform:
                return {"details": output}
        return {"details": {}}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Avg Job Duration
@router.get(
    "/average-job-duration",
    response_model=AverageJobDurationResponse,
    summary="Average Job Duration",
    description="""
Calcule la durée moyenne des jobs exécutés pour une **plateforme** donnée
sur une période spécifique.

- **date** : période d'analyse (ex: "24 hours ago", "1 week ago", etc.)
- **platform** : nom de la plateforme (ex: "google", "chatgpt")

La réponse retourne `average_duration` en **secondes**.
""",
    responses={
        200: {
            "description": "Average job duration successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "details": {"platform": "google", "average_duration": 12.5}
                    }
                }
            },
        },
        400: {"description": "Invalid date"},
        500: {"description": "Unable to execute the request"},
        422: {"description": "Validation Error"},
    },
)
def average_job_duration(
    date: DateOptions = Query(
        ..., description="Période à analyser", example="24 hours ago"
    ),
    platform: str = Query(..., description="Nom de la plateforme", example="google"),
):
    # Validation
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = get_average_job_duration(parsed_date)
        for output in outputs:
            if output["platform"] == platform:
                return {"details": output}
        return {"details": {}}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Avg Total Time per Prompt
@router.get(
    "/average-total-time-per-prompt",
    response_model=AverageTotalTimePerPromptResponse,
    summary="Average Total Time Per Prompt",
    description="""
Calcule le **temps moyen d'exécution total par prompt** sur une période donnée.

- **date** : période d'analyse (ex: "24 hours ago", "1 week ago", etc.)

La réponse retourne une liste où chaque élément contient :
- `prompt` : le nom ou type du prompt
- `average_duration` : la durée moyenne en **secondes**
""",
    responses={
        200: {
            "description": "Average total time per prompt successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "details": [
                            {"prompt": "Generate text", "average_duration": 3.45},
                            {"prompt": "Translate text", "average_duration": 5.20},
                        ]
                    }
                }
            },
        },
        400: {"description": "Invalid date"},
        500: {"description": "Unable to execute the request"},
        422: {"description": "Validation Error"},
    },
)
def average_total_time_per_prompt(
    date: DateOptions = Query(
        ..., description="Période à analyser", example="24 hours ago"
    ),
):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = get_average_total_time_per_prompt(parsed_date)
        return {"details": outputs}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Scraper Error Rate
@router.get(
    "/scraper-error-rate",
    response_model=ScraperErrorRateResponse,
    summary="Scraper Error Rate",
    description="""
Retourne le **taux d'erreurs des scrapers** pour une période donnée sur une plateforme spécifique.

- **date** : période d'analyse (ex: "24 hours ago", "1 week ago")
- **platform** : plateforme ciblée (ex: "google", "chatgpt")

La réponse inclut :
- `platform` : le nom de la plateforme
- `error_rate` : le taux d'erreur 
""",
    responses={
        200: {
            "description": "Scraper error rate successfully retrieved",
            "content": {
                "application/json": {
                    "example": {"details": {"platform": "google", "error_rate": 0.12}}
                }
            },
        },
        400: {"description": "Invalid date"},
        500: {"description": "Unable to execute the request"},
        422: {"description": "Validation Error"},
    },
)
def scraper_error_rate(
    date: DateOptions = Query(
        ..., description="Période d'analyse", example="24 hours ago"
    ),
    platform: str = Query(..., description="Nom de la plateforme", example="google"),
):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = get_scraper_error_rate(parsed_date)
        if not outputs:
            return {"details": outputs}
        for output in outputs:
            if output["platform"] == platform:
                return {"details": output}
        return {"details": {}}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Prompt Coverage Rate
@router.get(
    "/prompt-coverage-rate",
    response_model=PromptCoverageRateResponse,
    summary="Prompt Coverage Rate",
    description="""
Retourne le **taux de couverture des prompts** sur une période donnée.

- **date** : période d'analyse (ex: "24 hours ago", "1 week ago")

La réponse inclut une liste de prompts avec :
- `prompt` : le texte du prompt
- `coverage_rate` : le pourcentage de couverture 
""",
    responses={
        200: {
            "description": "Prompt coverage rate successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "details": [
                            {"prompt": "Find hotels in Paris", "coverage_rate": 0.85},
                            {
                                "prompt": "Restaurants in New York",
                                "coverage_rate": 0.92,
                            },
                        ]
                    }
                }
            },
        },
        400: {"description": "Invalid date"},
        500: {"description": "Unable to execute the request"},
        422: {"description": "Validation Error"},
    },
)
def prompt_coverage_rate(
    date: DateOptions = Query(
        ..., description="Période d'analyse", example="24 hours ago"
    ),
):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        output = get_prompt_coverage_rate(parsed_date)
        return {"details": output}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Last Run Timestamp per Platform
@router.get(
    "/last-run-timestamp",
    response_model=LastRunTimestampResponse,
    summary="Last Run Timestamp",
    description="""
Retourne le **dernier horodatage d'exécution** pour une plateforme spécifique.

- **platform** : nom de la plateforme (ex: "google", "chatgpt")

La réponse inclut :
- `platform` : la plateforme concernée
- `last_run_timestamp` : l'horodatage du dernier run (format ISO 8601)
""",
    responses={
        200: {
            "description": "Last run timestamp successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "details": {
                            "platform": "google",
                            "last_run_timestamp": "2025-09-17T10:15:30Z",
                        }
                    }
                }
            },
        },
        500: {"description": "Unable to execute the request"},
        422: {"description": "Validation Error"},
    },
)
def last_run_timestamp(
    platform: str = Query(..., description="Nom de la plateforme", example="google"),
):
    try:
        output = get_last_run_timestamp(platform)
        return {"details": output}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Total Running Jobs
@router.get(
    "/total-running-jobs",
    response_model=TotalRunningJobsResponse,
    summary="Total Running Jobs",
    description="""
Retourne le **nombre total de jobs actuellement en cours** sur une période donnée pour une plateforme spécifique.

- **date** : période d'analyse (ex: "24 hours ago", "1 week ago")  
- **platform** : nom de la plateforme (ex: "google", "chatgpt")  

La réponse inclut :
- `platform` : nom de la plateforme
- `total_running_jobs` : nombre de jobs en cours
""",
    responses={
        200: {
            "description": "Total running jobs successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "details": {"platform": "google", "total_running_jobs": 42}
                    }
                }
            },
        },
        400: {"description": "Invalid date"},
        500: {"description": "Unable to execute the request"},
        422: {"description": "Validation Error"},
    },
)
def total_running_jobs(
    date: DateOptions = Query(
        ..., description="Période d'analyse", example="24 hours ago"
    ),
    platform: str = Query(..., description="Nom de la plateforme", example="google"),
):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = get_total_running_jobs(parsed_date)
        if not outputs:
            return {"details": outputs}
        for output in outputs:
            if output["platform"] == platform:
                return {"details": output}
        return {"details": {}}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )
