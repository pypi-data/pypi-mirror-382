from dataclasses import dataclass

from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from ..schema import RedisearchSchema
from ..settings import RedisearchSettings


@dataclass
class RedisearchContext:
    """
    Redisearch context
    """

    settings: RedisearchSettings

    _schema: RedisearchSchema | None = None

    _redis: Redis | None = None

    _redis_async: AsyncRedis | None = None

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def schema(self) -> RedisearchSchema:
        """
        Redisearch index schema
        """
        if self._schema is None:
            if not self.settings.index_schema:
                raise ValueError("Index schema is not set in RedisearchSettings")

            self._schema = RedisearchSchema.from_field_dicts(self.settings.index_schema)

        return self._schema

    @schema.setter
    def schema(self, value: RedisearchSchema) -> None:
        self._schema = value

    # --------------------------------------------------

    @property
    def redis(self) -> Redis:
        if self._redis is None:
            raise ValueError("Redis client is not set in RedisearchContext")

        return self._redis

    @redis.setter
    def redis(self, value: Redis) -> None:
        self._redis = value

    # --------------------------------------------------

    @property
    def redis_async(self) -> AsyncRedis:
        if self._redis_async is None:
            raise ValueError("Async Redis client is not set in RedisearchContext")

        return self._redis_async

    @redis_async.setter
    def redis_async(self, value: AsyncRedis) -> None:
        self._redis_async = value
