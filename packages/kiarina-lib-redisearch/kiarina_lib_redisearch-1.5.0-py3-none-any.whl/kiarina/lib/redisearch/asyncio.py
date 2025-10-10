import logging
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._async.client import RedisearchClient
    from ._async.registry import create_redisearch_client
    from .settings import RedisearchSettings, settings_manager

__all__ = [
    "create_redisearch_client",
    "RedisearchClient",
    "RedisearchSettings",
    "settings_manager",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "create_redisearch_client": "._async.registry",
        "RedisearchClient": "._async.client",
        "RedisearchSettings": ".settings",
        "settings_manager": ".settings",
    }

    parent = __name__.rsplit(".", 1)[0]
    globals()[name] = getattr(import_module(module_map[name], parent), name)
    return globals()[name]
