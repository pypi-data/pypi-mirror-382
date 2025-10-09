from raystack.assets.v1beta1 import event_pb2 as _event_pb2
from raystack.assets.v1beta1 import lineage_pb2 as _lineage_pb2
from raystack.assets.v1beta1 import ownership_pb2 as _ownership_pb2
from raystack.assets.v1beta1 import properties_pb2 as _properties_pb2
from raystack.assets.v1beta1 import resource_pb2 as _resource_pb2
from raystack.assets.v1beta1 import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Dashboard(_message.Message):
    __slots__ = ("resource", "charts", "ownership", "properties", "timestamps", "lineage", "event")
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    CHARTS_FIELD_NUMBER: _ClassVar[int]
    OWNERSHIP_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    LINEAGE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    resource: _resource_pb2.Resource
    charts: _containers.RepeatedCompositeFieldContainer[Chart]
    ownership: _ownership_pb2.Ownership
    properties: _properties_pb2.Properties
    timestamps: _timestamp_pb2.Timestamp
    lineage: _lineage_pb2.Lineage
    event: _event_pb2.Event
    def __init__(self, resource: _Optional[_Union[_resource_pb2.Resource, _Mapping]] = ..., charts: _Optional[_Iterable[_Union[Chart, _Mapping]]] = ..., ownership: _Optional[_Union[_ownership_pb2.Ownership, _Mapping]] = ..., properties: _Optional[_Union[_properties_pb2.Properties, _Mapping]] = ..., timestamps: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., lineage: _Optional[_Union[_lineage_pb2.Lineage, _Mapping]] = ..., event: _Optional[_Union[_event_pb2.Event, _Mapping]] = ...) -> None: ...

class Chart(_message.Message):
    __slots__ = ("urn", "name", "type", "source", "description", "url", "raw_query", "data_source", "dashboard_urn", "dashboard_source", "ownership", "lineage", "properties", "timestamps", "event")
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    RAW_QUERY_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    DASHBOARD_URN_FIELD_NUMBER: _ClassVar[int]
    DASHBOARD_SOURCE_FIELD_NUMBER: _ClassVar[int]
    OWNERSHIP_FIELD_NUMBER: _ClassVar[int]
    LINEAGE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    urn: str
    name: str
    type: str
    source: str
    description: str
    url: str
    raw_query: str
    data_source: str
    dashboard_urn: str
    dashboard_source: str
    ownership: _ownership_pb2.Ownership
    lineage: _lineage_pb2.Lineage
    properties: _properties_pb2.Properties
    timestamps: _timestamp_pb2.Timestamp
    event: _event_pb2.Event
    def __init__(self, urn: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., source: _Optional[str] = ..., description: _Optional[str] = ..., url: _Optional[str] = ..., raw_query: _Optional[str] = ..., data_source: _Optional[str] = ..., dashboard_urn: _Optional[str] = ..., dashboard_source: _Optional[str] = ..., ownership: _Optional[_Union[_ownership_pb2.Ownership, _Mapping]] = ..., lineage: _Optional[_Union[_lineage_pb2.Lineage, _Mapping]] = ..., properties: _Optional[_Union[_properties_pb2.Properties, _Mapping]] = ..., timestamps: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., event: _Optional[_Union[_event_pb2.Event, _Mapping]] = ...) -> None: ...
