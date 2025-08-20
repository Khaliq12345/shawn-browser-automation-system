from fastapi import APIRouter
from src.utils.redis_utils import RedisBase
from src.utils.database import get_processes


router = APIRouter(prefix="/logs")


@router.get("/get-logs/{platform}")
def get_logs(platform: str):
    process_ids = get_processes(platform)
    logs = ""
    for process_id in process_ids:
        # Get Matching Instance
        redis_base = RedisBase(process_id)
        # Get Logs
        logs += redis_base.get_log()
    return logs
