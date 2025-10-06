import dateparser
from fastapi import APIRouter, HTTPException
from enum import Enum
from src.api.dependencies import databaseDepends

router = APIRouter(prefix="/metrics")


class DateOptions(str, Enum):
    hours_24 = "24 hours ago"
    one_week = "1 week ago"
    one_month = "1 month ago"
    one_year = "1 year ago"


# Job Success Rate
@router.get("/job-success-rate")
def job_success_rate(database: databaseDepends, date: DateOptions, platform: str):
    # Validation
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = database.get_job_success_rate(parsed_date)
        for output in outputs:
            if output["platform"] == platform:
                return {"details": output}
        return {"details": {}}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Avg Job Duration
@router.get("/average-job-duration")
def average_job_duration(database: databaseDepends, date: DateOptions, platform: str):
    # Validation
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = database.get_average_job_duration(parsed_date)
        for output in outputs:
            if output["platform"] == platform:
                return {"details": output}
        return {"details": {}}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Avg Total Time per Prompt
@router.get("/average-total-time-per-prompt")
def average_total_time_per_prompt(database: databaseDepends, date: DateOptions):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = database.get_average_total_time_per_prompt(parsed_date)
        return {"details": outputs}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Scraper Error Rate
@router.get("/scraper-error-rate")
def scraper_error_rate(database: databaseDepends, date: DateOptions, platform: str):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = database.get_scraper_error_rate(parsed_date)
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
@router.get("/prompt-coverage-rate")
def prompt_coverage_rate(database: databaseDepends, date: DateOptions):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        output = database.get_prompt_coverage_rate(parsed_date)
        return {"details": output}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Last Run Timestamp per Platform
@router.get("/last-run-timestamp")
def last_run_timestamp(database: databaseDepends, platform: str):
    try:
        output = database.get_last_run_timestamp(platform)
        return {"details": output}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to execute the request: {e}"
        )


# Total Running Jobs
@router.get("/total-running-jobs")
def total_running_jobs(database: databaseDepends, date: DateOptions, platform: str):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    try:
        outputs = database.get_total_running_jobs(parsed_date)
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
