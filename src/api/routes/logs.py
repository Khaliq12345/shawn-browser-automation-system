from fastapi import APIRouter, HTTPException, Path
from src.models.model import GetLogsResponse
from src.utils.redis_utils import RedisBase

router = APIRouter(prefix="/logs")


@router.get(
    "/{process_id}",
    response_model=GetLogsResponse,
    summary="Get Logs for a Process",
    description="""
Récupère les logs complets d’un processus donné par son ID.

- **process_id** : identifiant du processus.
- La réponse contient une liste de lignes de logs.
""",
    responses={
        200: {
            "description": "Logs retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "details": [
                            "2025-09-17 12:00:01 [INFO] Process started",
                            "2025-09-17 12:00:05 [INFO] Step 1 completed",
                            "2025-09-17 12:01:12 [ERROR] Step 2 failed",
                        ]
                    }
                }
            },
        },
        500: {"description": "Unable to retrieve logs"},
        422: {"description": "Validation Error"},
    },
)
def get_logs(process_id: str = Path(..., description="Identifiant du processus", example="google_1694948567")):
    try:
        # Get Matching Instance
        redis_base = RedisBase(process_id)
        # Get Logs
        logs = redis_base.get_log()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve Logs : {e}")
    return {"details": logs}
