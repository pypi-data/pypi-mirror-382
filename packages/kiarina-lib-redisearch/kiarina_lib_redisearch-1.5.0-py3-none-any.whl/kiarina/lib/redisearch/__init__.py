import logging
from importlib import import_module
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._sync.client import RedisearchClient
    from ._sync.registry import create_redisearch_client
    from .settings import RedisearchSettings, settings_manager

__version__ = version("kiarina-lib-redisearch")

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
        "create_redisearch_client": "._sync.registry",
        "RedisearchClient": "._sync.client",
        "RedisearchSettings": ".settings",
        "settings_manager": ".settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
