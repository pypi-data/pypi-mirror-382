from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class RedisearchSettings(BaseSettings):
    """
    Redisearch settings
    """

    model_config = SettingsConfigDict(env_prefix="KIARINA_LIB_REDISEARCH_")

    key_prefix: str = ""
    """
    Redis key prefix

    The prefix for keys of documents registered with Redisearch.
    Specify a string ending with a colon. e.g. "myapp:"
    """

    index_name: str = "default"
    """
    Redisearch index name

    Only alphanumeric characters, underscores, hyphens, and periods.
    The beginning consists solely of letters.
    """

    index_schema: list[dict[str, Any]] | None = None
    """
    Redisearch index schema

    RedisearchSchema.from_field_dicts can be used to
    create the schema from a list of field dictionaries.
    """

    protect_index_deletion: bool = False
    """
    Protect index deletion

    When set to True, the delete_index operation is protected,
    preventing the index from being accidentally deleted.
    """


settings_manager = SettingsManager(RedisearchSettings, multi=True)
