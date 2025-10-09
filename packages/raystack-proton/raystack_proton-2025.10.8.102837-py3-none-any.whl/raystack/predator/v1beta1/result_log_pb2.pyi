import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from raystack.predator.v1beta1 import metrics_log_pb2 as _metrics_log_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResultLogKey(_message.Message):
    __slots__ = ("id", "group", "event_timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    EVENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    group: _metrics_log_pb2.Group
    event_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., group: _Optional[_Union[_metrics_log_pb2.Group, _Mapping]] = ..., event_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ResultLogMessage(_message.Message):
    __slots__ = ("id", "profile_id", "urn", "group", "results", "event_timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROFILE_ID_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    EVENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    profile_id: str
    urn: str
    group: _metrics_log_pb2.Group
    results: _containers.RepeatedCompositeFieldContainer[Result]
    event_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., profile_id: _Optional[str] = ..., urn: _Optional[str] = ..., group: _Optional[_Union[_metrics_log_pb2.Group, _Mapping]] = ..., results: _Optional[_Iterable[_Union[Result, _Mapping]]] = ..., event_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Result(_message.Message):
    __slots__ = ("name", "field_id", "value", "rules", "pass_flag", "condition")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FIELD_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    RULES_FIELD_NUMBER: _ClassVar[int]
    PASS_FLAG_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    name: str
    field_id: str
    value: float
    rules: _containers.RepeatedCompositeFieldContainer[ToleranceRule]
    pass_flag: bool
    condition: str
    def __init__(self, name: _Optional[str] = ..., field_id: _Optional[str] = ..., value: _Optional[float] = ..., rules: _Optional[_Iterable[_Union[ToleranceRule, _Mapping]]] = ..., pass_flag: _Optional[bool] = ..., condition: _Optional[str] = ...) -> None: ...

class ToleranceRule(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: float
    def __init__(self, name: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
