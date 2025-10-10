"""
Module for constructing filter queries for Redisearch

RedisearchFilter can be combined using & and | operators to create
complex logical expressions that are evaluated in the Redis Query language.

This interface allows users to construct complex queries without needing to know
the Redis Query language.

Filter-based fields are not initialised directly.
Instead, they are constructed by combining RedisFilterFields
using the & and | operators.

Examples:
    >>> import kiarina.lib.redisearch.filter as rf
    >>> filter = (rf.Tag("color") == "blue") & (rf.Numeric("price") < 100)
    >>> print(str(filter))
    (@color:{blue} @price:[-inf (100)])

All examples:
    >>> import kiarina.lib.redisearch.filter as rf
    >>>
    >>> rf.Tag("color") == "blue"
    >>> rf.Tag("color") == ["blue", "red"]
    >>> rf.Tag("color") != "blue"
    >>> rf.Tag("color") != ["blue", "red"]
    >>>
    >>> rf.Numeric("price") == 100
    >>> rf.Numeric("price") != 100
    >>> rf.Numeric("price") > 100
    >>> rf.Numeric("price") < 100
    >>> rf.Numeric("price") >= 100
    >>> rf.Numeric("price") <= 100
    >>>
    >>> rf.Text("title") == "hello"
    >>> rf.Text("title") != "hello"
    >>> rf.Text("title") % "*hello*"
    >>>
    >>> (rf.Tag("color") == "blue") & (rf.Numeric("price") < 100)
    >>> (rf.Tag("color") == "blue") | (rf.Numeric("price")
"""

from ._field.numeric import Numeric
from ._field.tag import Tag
from ._field.text import Text
from ._model import RedisearchFilter
from ._registry import create_redisearch_filter
from ._types import RedisearchFilterConditions

__all__ = [
    # ._field
    "Numeric",
    "Tag",
    "Text",
    # ._model
    "RedisearchFilter",
    # ._registry
    "create_redisearch_filter",
    # ._types
    "RedisearchFilterConditions",
]
