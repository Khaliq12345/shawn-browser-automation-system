from datetime import datetime
from scr.utils import celery_app
from fastapi import HTTPException, APIRouter
from src.api.dependencies import databaseDepends

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
        result = database.delete_schedule(prompt_id=prompt_id, brand_report_id=brand_report_id)
        if result:
            return {"status": "success", "message": "Schedule deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Schedule not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
