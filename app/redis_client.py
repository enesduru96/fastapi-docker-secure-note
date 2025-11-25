import redis.asyncio as redis
from .config import settings

redis_pool = None

def get_redis_pool():
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
            encoding="utf-8",
        )
    return redis_pool

async def close_redis_pool():
    global redis_pool
    if redis_pool:
        await redis_pool.aclose()
        redis_pool = None