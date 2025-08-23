from fastapi import APIRouter
from src.utils.redis_utils import AsyncRedisBase

router = APIRouter(prefix="/logs")


@router.get("/{process_id}")
async def get_logs(process_id: str):
    # Get Matching Instance
    redis_base = AsyncRedisBase(process_id)
    # Get Logs
    logs = await redis_base.get_log()
    return {"details": logs}
