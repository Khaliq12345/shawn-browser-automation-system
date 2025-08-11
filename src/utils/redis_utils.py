import redis.asyncio as redis


class RedisBaseAsync:
    def __init__(self, redis_host="localhost", redis_port=6379, redis_db=0):
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db, decode_responses=True
        )

    # To set a log
    async def set_log(self, process_id: str, message: str, expire_seconds: int = 3600):
        old = await self.redis_client.get(process_id)
        old = old if old else ""
        new_value = f"{old}\n{message}" if old else message
        await self.redis_client.set(process_id, new_value, ex=expire_seconds)

    # To retrieve a log
    async def get_log(self, process_id: str) -> str:
        value = await self.redis_client.get(process_id)
        return value if value else ""


class RedisChatGPT(RedisBaseAsync):
    def __init__(self):
        super().__init__(redis_host="localhost", redis_port=6379, redis_db=1)


class RedisGemini(RedisBaseAsync):
    def __init__(self):
        super().__init__(redis_host="localhost", redis_port=6379, redis_db=2)


class RedisPerplexity(RedisBaseAsync):
    def __init__(self):
        super().__init__(redis_host="localhost", redis_port=6379, redis_db=3)


# To get the matching class instance from nam
def get_redis_instance(name: str):
    all_class = {
        "chatgpt": RedisChatGPT,
        "gemini": RedisGemini,
        "perplexity": RedisPerplexity,
    }
    if name not in all_class:
        return None
    return all_class[name]()
