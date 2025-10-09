from raystack.assets.v1beta1 import properties_pb2 as _properties_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Columns(_message.Message):
    __slots__ = ("columns",)
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    columns: _containers.RepeatedCompositeFieldContainer[Column]
    def __init__(self, columns: _Optional[_Iterable[_Union[Column, _Mapping]]] = ...) -> None: ...

class Column(_message.Message):
    __slots__ = ("name", "description", "data_type", "is_nullable", "length", "profile", "properties")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_NULLABLE_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    data_type: str
    is_nullable: bool
    length: int
    profile: ColumnProfile
    properties: _properties_pb2.Properties
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., data_type: _Optional[str] = ..., is_nullable: _Optional[bool] = ..., length: _Optional[int] = ..., profile: _Optional[_Union[ColumnProfile, _Mapping]] = ..., properties: _Optional[_Union[_properties_pb2.Properties, _Mapping]] = ...) -> None: ...

class ColumnProfile(_message.Message):
    __slots__ = ("min", "max", "avg", "med", "unique", "count", "top")
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    AVG_FIELD_NUMBER: _ClassVar[int]
    MED_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TOP_FIELD_NUMBER: _ClassVar[int]
    min: str
    max: str
    avg: float
    med: float
    unique: int
    count: int
    top: str
    def __init__(self, min: _Optional[str] = ..., max: _Optional[str] = ..., avg: _Optional[float] = ..., med: _Optional[float] = ..., unique: _Optional[int] = ..., count: _Optional[int] = ..., top: _Optional[str] = ...) -> None: ...

class TopicSchema(_message.Message):
    __slots__ = ("schema_url", "format")
    SCHEMA_URL_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    schema_url: str
    format: str
    def __init__(self, schema_url: _Optional[str] = ..., format: _Optional[str] = ...) -> None: ...
