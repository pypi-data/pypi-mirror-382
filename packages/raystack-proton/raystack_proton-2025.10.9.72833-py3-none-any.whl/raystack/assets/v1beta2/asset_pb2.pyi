import datetime

from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from raystack.assets.v1beta2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Asset(_message.Message):
    __slots__ = ("urn", "name", "service", "type", "url", "description", "data", "owners", "lineage", "labels", "event", "create_time", "update_time")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    OWNERS_FIELD_NUMBER: _ClassVar[int]
    LINEAGE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    urn: str
    name: str
    service: str
    type: str
    url: str
    description: str
    data: _any_pb2.Any
    owners: _containers.RepeatedCompositeFieldContainer[_common_pb2.Owner]
    lineage: _common_pb2.Lineage
    labels: _containers.ScalarMap[str, str]
    event: _common_pb2.Event
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    def __init__(self, urn: _Optional[str] = ..., name: _Optional[str] = ..., service: _Optional[str] = ..., type: _Optional[str] = ..., url: _Optional[str] = ..., description: _Optional[str] = ..., data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., owners: _Optional[_Iterable[_Union[_common_pb2.Owner, _Mapping]]] = ..., lineage: _Optional[_Union[_common_pb2.Lineage, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., event: _Optional[_Union[_common_pb2.Event, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
