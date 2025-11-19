from fastapi import APIRouter, HTTPException

from src.api.dependencies import databaseDepends

router = APIRouter(prefix="/reports")


# Job Success Rate
@router.get("/")
def get_report(database: databaseDepends, limit: int = 20, page: int = 1):
    try:
        offset = (page - 1) * limit
        reports = database.get_reports(limit, offset)
        return reports
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Server Error - Unable to execute the request: {e}"
        )
