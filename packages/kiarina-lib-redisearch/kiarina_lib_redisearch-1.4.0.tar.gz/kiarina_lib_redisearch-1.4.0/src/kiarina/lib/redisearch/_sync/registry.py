import redis

from ..settings import settings_manager
from .client import RedisearchClient


def create_redisearch_client(
    config_key: str | None = None,
    *,
    redis: redis.Redis,
) -> RedisearchClient:
    """
    Create a Redisearch client.
    """
    settings = settings_manager.get_settings_by_key(config_key)
    return RedisearchClient(settings, redis=redis)
