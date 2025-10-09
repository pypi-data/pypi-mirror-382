from raystack.assets.v1beta1 import event_pb2 as _event_pb2
from raystack.assets.v1beta1 import lineage_pb2 as _lineage_pb2
from raystack.assets.v1beta1 import ownership_pb2 as _ownership_pb2
from raystack.assets.v1beta1 import preview_pb2 as _preview_pb2
from raystack.assets.v1beta1 import properties_pb2 as _properties_pb2
from raystack.assets.v1beta1 import resource_pb2 as _resource_pb2
from raystack.assets.v1beta1 import schema_pb2 as _schema_pb2
from raystack.assets.v1beta1 import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Table(_message.Message):
    __slots__ = ("resource", "profile", "schema", "preview", "ownership", "lineage", "properties", "timestamps", "event")
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    OWNERSHIP_FIELD_NUMBER: _ClassVar[int]
    LINEAGE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    resource: _resource_pb2.Resource
    profile: TableProfile
    schema: _schema_pb2.Columns
    preview: _preview_pb2.Preview
    ownership: _ownership_pb2.Ownership
    lineage: _lineage_pb2.Lineage
    properties: _properties_pb2.Properties
    timestamps: _timestamp_pb2.Timestamp
    event: _event_pb2.Event
    def __init__(self, resource: _Optional[_Union[_resource_pb2.Resource, _Mapping]] = ..., profile: _Optional[_Union[TableProfile, _Mapping]] = ..., schema: _Optional[_Union[_schema_pb2.Columns, _Mapping]] = ..., preview: _Optional[_Union[_preview_pb2.Preview, _Mapping]] = ..., ownership: _Optional[_Union[_ownership_pb2.Ownership, _Mapping]] = ..., lineage: _Optional[_Union[_lineage_pb2.Lineage, _Mapping]] = ..., properties: _Optional[_Union[_properties_pb2.Properties, _Mapping]] = ..., timestamps: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., event: _Optional[_Union[_event_pb2.Event, _Mapping]] = ...) -> None: ...

class TableProfile(_message.Message):
    __slots__ = ("total_rows", "partition_key", "partition_value", "usage_count", "joins", "filters")
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    PARTITION_KEY_FIELD_NUMBER: _ClassVar[int]
    PARTITION_VALUE_FIELD_NUMBER: _ClassVar[int]
    USAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    JOINS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    total_rows: int
    partition_key: str
    partition_value: str
    usage_count: int
    joins: _containers.RepeatedCompositeFieldContainer[Join]
    filters: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, total_rows: _Optional[int] = ..., partition_key: _Optional[str] = ..., partition_value: _Optional[str] = ..., usage_count: _Optional[int] = ..., joins: _Optional[_Iterable[_Union[Join, _Mapping]]] = ..., filters: _Optional[_Iterable[str]] = ...) -> None: ...

class Join(_message.Message):
    __slots__ = ("urn", "count", "conditions")
    URN_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    urn: str
    count: int
    conditions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, urn: _Optional[str] = ..., count: _Optional[int] = ..., conditions: _Optional[_Iterable[str]] = ...) -> None: ...
