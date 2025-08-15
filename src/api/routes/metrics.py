import dateparser
from fastapi import APIRouter, HTTPException
from typing import Optional
from enum import Enum
from src.utils.database import get_job_success_rate


router = APIRouter(prefix="/metrics")


class DateOptions(str, Enum):
    hours_24 = "24 hours"
    one_week = "1 week"
    one_month = "1 month"
    one_year = "1 year"


@router.get("/job-success-rate")
def job_success_rate(date: DateOptions, platform: Optional[str] = None):
    # Convertir la chaîne en datetime avec dateparser
    date_str = date.value
    parsed_date = dateparser.parse(
        date_str, settings={"RETURN_AS_TIMEZONE_AWARE": True}
    )
    # Validation
    if not parsed_date:
        raise HTTPException(status_code=400, detail="Impossible de parser la date")
    return get_job_success_rate(platform, parsed_date)
