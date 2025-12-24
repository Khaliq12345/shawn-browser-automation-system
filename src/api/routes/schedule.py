from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Query

from src.models.model import Prompt
from src.api.dependencies import databaseDepends

router = APIRouter(prefix="/schedule")


@router.get("/")
def get_schedules(database: databaseDepends, page: int = 1, limit: int = 10):
    """Get Schedules"""
    try:
        offset = limit * (page - 1)
        response = database.get_schedules(limit=limit, offset=offset)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            return {
                "status": "success",
                "message": "Schedule deleted successfully",
            }
        else:
            raise HTTPException(status_code=404, detail="Schedule not found")
    except HTTPException as _:
        raise
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

@router.post("/add")
def add_schedules(database: databaseDepends, prompt_details: List[Prompt], brand_report_id: str) -> dict:
    """Add more prompts to brand report"""
    try:
        database.add_schedules(
            prompts=prompt_details,
            brand_report_id=brand_report_id,
        )
        return {
            "status": "success",
            "message": "Schedule added successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
