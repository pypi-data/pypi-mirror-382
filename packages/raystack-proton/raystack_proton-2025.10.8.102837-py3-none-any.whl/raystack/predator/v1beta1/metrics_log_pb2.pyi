import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MetricsLogKey(_message.Message):
    __slots__ = ("id", "group", "event_timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    EVENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    group: Group
    event_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., group: _Optional[_Union[Group, _Mapping]] = ..., event_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MetricsLogMessage(_message.Message):
    __slots__ = ("id", "urn", "filter", "group", "mode", "table_metrics", "column_metrics", "event_timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    TABLE_METRICS_FIELD_NUMBER: _ClassVar[int]
    COLUMN_METRICS_FIELD_NUMBER: _ClassVar[int]
    EVENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    urn: str
    filter: str
    group: Group
    mode: str
    table_metrics: _containers.RepeatedCompositeFieldContainer[Metric]
    column_metrics: _containers.RepeatedCompositeFieldContainer[ColumnMetric]
    event_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., urn: _Optional[str] = ..., filter: _Optional[str] = ..., group: _Optional[_Union[Group, _Mapping]] = ..., mode: _Optional[str] = ..., table_metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ..., column_metrics: _Optional[_Iterable[_Union[ColumnMetric, _Mapping]]] = ..., event_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Metric(_message.Message):
    __slots__ = ("name", "value", "condition")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: float
    condition: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[float] = ..., condition: _Optional[str] = ...) -> None: ...

class Group(_message.Message):
    __slots__ = ("column", "value")
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    column: str
    value: str
    def __init__(self, column: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ColumnMetric(_message.Message):
    __slots__ = ("id", "type", "metrics")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    metrics: _containers.RepeatedCompositeFieldContainer[Metric]
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ...) -> None: ...
