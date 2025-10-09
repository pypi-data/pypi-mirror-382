import datetime

from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from raystack.assets.v1beta2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Dashboard(_message.Message):
    __slots__ = ("charts", "attributes", "create_time", "update_time")
    CHARTS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    charts: _containers.RepeatedCompositeFieldContainer[Chart]
    attributes: _struct_pb2.Struct
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    def __init__(self, charts: _Optional[_Iterable[_Union[Chart, _Mapping]]] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Chart(_message.Message):
    __slots__ = ("urn", "name", "type", "source", "description", "url", "raw_query", "data_source", "dashboard_urn", "dashboard_source", "owners", "attributes", "lineage", "create_time", "update_time", "event")
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
    OWNERS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    LINEAGE_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
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
    owners: _containers.RepeatedCompositeFieldContainer[_common_pb2.Owner]
    attributes: _struct_pb2.Struct
    lineage: _common_pb2.Lineage
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    event: _common_pb2.Event
    def __init__(self, urn: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., source: _Optional[str] = ..., description: _Optional[str] = ..., url: _Optional[str] = ..., raw_query: _Optional[str] = ..., data_source: _Optional[str] = ..., dashboard_urn: _Optional[str] = ..., dashboard_source: _Optional[str] = ..., owners: _Optional[_Iterable[_Union[_common_pb2.Owner, _Mapping]]] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., lineage: _Optional[_Union[_common_pb2.Lineage, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., event: _Optional[_Union[_common_pb2.Event, _Mapping]] = ...) -> None: ...
