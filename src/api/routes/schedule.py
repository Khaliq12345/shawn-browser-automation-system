from datetime import datetime
from fastapi import HTTPException, APIRouter, Query
from typing import Annotated, List
from src.api.dependencies import databaseDepends
from src.utils import celery_app

router = APIRouter(prefix="/schedule")


@router.delete("/delete")
def delete_schedule(
    prompt_id: str,
    brand_report_id: str,
    database: databaseDepends,
):
    """
    Delete a schedule entry based on prompt_id and brand_report_id.
    """
    try:
        result = database.delete_schedule(
            prompt_id=prompt_id, brand_report_id=brand_report_id
        )
        if result:
            return {"status": "success", "message": "Schedule deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Schedule not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/next-runs")
def get_next_runs(
    prompt_ids: Annotated[List[str], Query()],
    database: databaseDepends,
):
    """
    Get the next_run timestamps for a list of prompt_ids.
    """
    try:
        next_runs = database.get_next_runs(prompt_ids)
        return next_runs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

