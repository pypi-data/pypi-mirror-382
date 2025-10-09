import datetime

from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Table(_message.Message):
    __slots__ = ("profile", "columns", "preview_fields", "preview_rows", "attributes", "create_time", "update_time")
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELDS_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_ROWS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    profile: TableProfile
    columns: _containers.RepeatedCompositeFieldContainer[Column]
    preview_fields: _containers.RepeatedScalarFieldContainer[str]
    preview_rows: _struct_pb2.ListValue
    attributes: _struct_pb2.Struct
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    def __init__(self, profile: _Optional[_Union[TableProfile, _Mapping]] = ..., columns: _Optional[_Iterable[_Union[Column, _Mapping]]] = ..., preview_fields: _Optional[_Iterable[str]] = ..., preview_rows: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TableProfile(_message.Message):
    __slots__ = ("total_rows", "partition_key", "partition_value", "usage_count", "common_joins", "filters")
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    PARTITION_KEY_FIELD_NUMBER: _ClassVar[int]
    PARTITION_VALUE_FIELD_NUMBER: _ClassVar[int]
    USAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    COMMON_JOINS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    total_rows: int
    partition_key: str
    partition_value: str
    usage_count: int
    common_joins: _containers.RepeatedCompositeFieldContainer[TableCommonJoin]
    filters: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, total_rows: _Optional[int] = ..., partition_key: _Optional[str] = ..., partition_value: _Optional[str] = ..., usage_count: _Optional[int] = ..., common_joins: _Optional[_Iterable[_Union[TableCommonJoin, _Mapping]]] = ..., filters: _Optional[_Iterable[str]] = ...) -> None: ...

class TableCommonJoin(_message.Message):
    __slots__ = ("urn", "count", "conditions")
    URN_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    urn: str
    count: int
    conditions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, urn: _Optional[str] = ..., count: _Optional[int] = ..., conditions: _Optional[_Iterable[str]] = ...) -> None: ...

class Column(_message.Message):
    __slots__ = ("name", "description", "data_type", "is_nullable", "length", "profile", "columns", "attributes")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_NULLABLE_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    data_type: str
    is_nullable: bool
    length: int
    profile: ColumnProfile
    columns: _containers.RepeatedCompositeFieldContainer[Column]
    attributes: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., data_type: _Optional[str] = ..., is_nullable: _Optional[bool] = ..., length: _Optional[int] = ..., profile: _Optional[_Union[ColumnProfile, _Mapping]] = ..., columns: _Optional[_Iterable[_Union[Column, _Mapping]]] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

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
