"""
フィールド名に `payload`, `distance` は使用できません。
フィールド名に `id` を使用する場合、ドキュメントの ID と同じ値として扱われます。
"""

from ._field.numeric import NumericFieldSchema
from ._field.tag import TagFieldSchema
from ._field.text import TextFieldSchema
from ._field.vector.flat import FlatVectorFieldSchema
from ._field.vector.hnsw import HNSWVectorFieldSchema
from ._model import RedisearchSchema
from ._types import FieldSchema

__all__ = [
    # ._field
    "FlatVectorFieldSchema",
    "HNSWVectorFieldSchema",
    "NumericFieldSchema",
    "TagFieldSchema",
    "TextFieldSchema",
    # ._model
    "RedisearchSchema",
    # ._types
    "FieldSchema",
]
