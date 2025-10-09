import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Event(_message.Message):
    __slots__ = ("timestamp", "action", "description")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    action: str
    description: str
    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., action: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class Lineage(_message.Message):
    __slots__ = ("upstreams", "downstreams")
    UPSTREAMS_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAMS_FIELD_NUMBER: _ClassVar[int]
    upstreams: _containers.RepeatedCompositeFieldContainer[Resource]
    downstreams: _containers.RepeatedCompositeFieldContainer[Resource]
    def __init__(self, upstreams: _Optional[_Iterable[_Union[Resource, _Mapping]]] = ..., downstreams: _Optional[_Iterable[_Union[Resource, _Mapping]]] = ...) -> None: ...

class Resource(_message.Message):
    __slots__ = ("urn", "name", "service", "type")
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    urn: str
    name: str
    service: str
    type: str
    def __init__(self, urn: _Optional[str] = ..., name: _Optional[str] = ..., service: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class Owner(_message.Message):
    __slots__ = ("urn", "name", "role", "email")
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    urn: str
    name: str
    role: str
    email: str
    def __init__(self, urn: _Optional[str] = ..., name: _Optional[str] = ..., role: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...
