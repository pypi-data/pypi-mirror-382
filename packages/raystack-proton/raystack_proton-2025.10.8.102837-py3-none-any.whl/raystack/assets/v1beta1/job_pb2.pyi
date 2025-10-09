from raystack.assets.v1beta1 import event_pb2 as _event_pb2
from raystack.assets.v1beta1 import lineage_pb2 as _lineage_pb2
from raystack.assets.v1beta1 import ownership_pb2 as _ownership_pb2
from raystack.assets.v1beta1 import properties_pb2 as _properties_pb2
from raystack.assets.v1beta1 import resource_pb2 as _resource_pb2
from raystack.assets.v1beta1 import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Job(_message.Message):
    __slots__ = ("resource", "ownership", "lineage", "properties", "timestamps", "event")
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    OWNERSHIP_FIELD_NUMBER: _ClassVar[int]
    LINEAGE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    resource: _resource_pb2.Resource
    ownership: _ownership_pb2.Ownership
    lineage: _lineage_pb2.Lineage
    properties: _properties_pb2.Properties
    timestamps: _timestamp_pb2.Timestamp
    event: _event_pb2.Event
    def __init__(self, resource: _Optional[_Union[_resource_pb2.Resource, _Mapping]] = ..., ownership: _Optional[_Union[_ownership_pb2.Ownership, _Mapping]] = ..., lineage: _Optional[_Union[_lineage_pb2.Lineage, _Mapping]] = ..., properties: _Optional[_Union[_properties_pb2.Properties, _Mapping]] = ..., timestamps: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., event: _Optional[_Union[_event_pb2.Event, _Mapping]] = ...) -> None: ...
