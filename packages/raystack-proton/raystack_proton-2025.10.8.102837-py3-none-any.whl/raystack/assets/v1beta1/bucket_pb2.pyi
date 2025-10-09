import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from raystack.assets.v1beta1 import event_pb2 as _event_pb2
from raystack.assets.v1beta1 import ownership_pb2 as _ownership_pb2
from raystack.assets.v1beta1 import properties_pb2 as _properties_pb2
from raystack.assets.v1beta1 import resource_pb2 as _resource_pb2
from raystack.assets.v1beta1 import timestamp_pb2 as _timestamp_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Bucket(_message.Message):
    __slots__ = ("resource", "description", "location", "storage_type", "blobs", "ownership", "properties", "timestamps", "event")
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    STORAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    BLOBS_FIELD_NUMBER: _ClassVar[int]
    OWNERSHIP_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    resource: _resource_pb2.Resource
    description: str
    location: str
    storage_type: str
    blobs: _containers.RepeatedCompositeFieldContainer[Blob]
    ownership: _ownership_pb2.Ownership
    properties: _properties_pb2.Properties
    timestamps: _timestamp_pb2_1.Timestamp
    event: _event_pb2.Event
    def __init__(self, resource: _Optional[_Union[_resource_pb2.Resource, _Mapping]] = ..., description: _Optional[str] = ..., location: _Optional[str] = ..., storage_type: _Optional[str] = ..., blobs: _Optional[_Iterable[_Union[Blob, _Mapping]]] = ..., ownership: _Optional[_Union[_ownership_pb2.Ownership, _Mapping]] = ..., properties: _Optional[_Union[_properties_pb2.Properties, _Mapping]] = ..., timestamps: _Optional[_Union[_timestamp_pb2_1.Timestamp, _Mapping]] = ..., event: _Optional[_Union[_event_pb2.Event, _Mapping]] = ...) -> None: ...

class Blob(_message.Message):
    __slots__ = ("urn", "name", "source", "size", "delete_time", "expire_time", "ownership", "properties", "timestamps")
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    DELETE_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_TIME_FIELD_NUMBER: _ClassVar[int]
    OWNERSHIP_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    urn: str
    name: str
    source: str
    size: int
    delete_time: _timestamp_pb2.Timestamp
    expire_time: _timestamp_pb2.Timestamp
    ownership: _ownership_pb2.Ownership
    properties: _properties_pb2.Properties
    timestamps: _timestamp_pb2_1.Timestamp
    def __init__(self, urn: _Optional[str] = ..., name: _Optional[str] = ..., source: _Optional[str] = ..., size: _Optional[int] = ..., delete_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expire_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., ownership: _Optional[_Union[_ownership_pb2.Ownership, _Mapping]] = ..., properties: _Optional[_Union[_properties_pb2.Properties, _Mapping]] = ..., timestamps: _Optional[_Union[_timestamp_pb2_1.Timestamp, _Mapping]] = ...) -> None: ...
