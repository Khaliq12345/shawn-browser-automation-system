import dateparser
from fastapi import APIRouter, HTTPException
from typing import Optional
from enum import Enum
from src.utils.database import (
    get_job_success_rate,
    get_average_job_duration,
    get_average_total_time_per_prompt,
    get_scraper_error_rate,
    get_prompt_coverage_rate,
    get_last_run_timestamp,
)


router = APIRouter(prefix="/metrics")


class DateOptions(str, Enum):
    hours_24 = "24 hours ago"
    one_week = "1 week ago"
    one_month = "1 month ago"
    one_year = "1 year ago"


# Job Success Rate
@router.get("/job-success-rate")
async def job_success_rate(date: DateOptions, platform: Optional[str] = None):
    # Validation
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    outputs = await get_job_success_rate(parsed_date)
    for output in outputs:
        if output["platform"] == platform:
            return {"details": output}
    return {"details": outputs}


# Avg Job Duration
@router.get("/average-job-duration")
async def average_job_duration(date: DateOptions, platform: Optional[str] = None):
    # Validation
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    outputs = await get_average_job_duration(parsed_date)
    for output in outputs:
        if output["platform"] == platform:
            return {"details": output}
    return {"details": outputs}


# Avg Total Time per Prompt
@router.get("/average-total-time-per-prompt")
async def average_total_time_per_prompt(date: DateOptions):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    outputs = await get_average_total_time_per_prompt(parsed_date)
    return {"details": outputs}


# Scraper Error Rate
@router.get("/scraper-error-rate")
async def scraper_error_rate(date: DateOptions, platform: Optional[str] = None):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    outputs = await get_scraper_error_rate(parsed_date)
    if not outputs:
        return {"details": outputs}
    for output in outputs:
        if output["platform"] == platform:
            return {"details": output}
    return {"details": outputs}


# Prompt Coverage Rate
@router.get("/prompt-coverage-rate")
async def prompt_coverage_rate(date: DateOptions):
    parsed_date = dateparser.parse(
        date.value, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    output = await get_prompt_coverage_rate(parsed_date)
    return {"details": output}


# Last Run Timestamp per Platform
@router.get("/last-run-timestamp")
async def last_run_timestamp(platform: str):
    output = await get_last_run_timestamp(platform)
    return {"details": output}
