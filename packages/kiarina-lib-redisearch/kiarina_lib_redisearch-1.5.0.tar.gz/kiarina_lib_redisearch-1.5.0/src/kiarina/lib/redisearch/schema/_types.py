from typing import TypeAlias

from ._field.numeric import NumericFieldSchema
from ._field.tag import TagFieldSchema
from ._field.text import TextFieldSchema
from ._field.vector.flat import FlatVectorFieldSchema
from ._field.vector.hnsw import HNSWVectorFieldSchema

FieldSchema: TypeAlias = (
    NumericFieldSchema
    | TagFieldSchema
    | TextFieldSchema
    | FlatVectorFieldSchema
    | HNSWVectorFieldSchema
)
"""Type of the field schema"""
