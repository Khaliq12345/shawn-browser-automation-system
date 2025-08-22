from fastapi import APIRouter
from src.utils.redis_utils import AsyncRedisBase
from src.utils.database import get_all_platform_processes


router = APIRouter(prefix="/logs")


@router.get("/get-logs/{platform}")
async def get_logs(platform: str):
    process_ids = await get_all_platform_processes(platform)
    logs = ""
    for process_id in process_ids:
        # Get Matching Instance
        redis_base = AsyncRedisBase(process_id)
        # Get Logs
        logs += await redis_base.get_log()
    return logs
