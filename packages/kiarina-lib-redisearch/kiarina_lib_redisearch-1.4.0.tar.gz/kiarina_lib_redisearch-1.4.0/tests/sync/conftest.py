import pytest

from kiarina.lib.redis import get_redis
from kiarina.lib.redisearch import RedisearchClient, RedisearchSettings


@pytest.fixture
def redis():
    return get_redis(cache_key="kiarina.lib.redisearch")


@pytest.fixture
def client(key_prefix, index_name, redis, fields):
    return RedisearchClient(
        RedisearchSettings(
            key_prefix=key_prefix,
            index_name=index_name,
            index_schema=fields,
        ),
        redis=redis,
    )
