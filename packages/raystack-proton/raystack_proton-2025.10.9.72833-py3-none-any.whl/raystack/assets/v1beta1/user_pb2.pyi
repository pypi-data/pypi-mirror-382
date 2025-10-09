from raystack.assets.v1beta1 import event_pb2 as _event_pb2
from raystack.assets.v1beta1 import properties_pb2 as _properties_pb2
from raystack.assets.v1beta1 import resource_pb2 as _resource_pb2
from raystack.assets.v1beta1 import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("resource", "email", "username", "first_name", "last_name", "full_name", "display_name", "title", "status", "manager_email", "profiles", "memberships", "properties", "timestamps", "event")
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MANAGER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    PROFILES_FIELD_NUMBER: _ClassVar[int]
    MEMBERSHIPS_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    resource: _resource_pb2.Resource
    email: str
    username: str
    first_name: str
    last_name: str
    full_name: str
    display_name: str
    title: str
    status: str
    manager_email: str
    profiles: _containers.RepeatedCompositeFieldContainer[Profile]
    memberships: _containers.RepeatedCompositeFieldContainer[Membership]
    properties: _properties_pb2.Properties
    timestamps: _timestamp_pb2.Timestamp
    event: _event_pb2.Event
    def __init__(self, resource: _Optional[_Union[_resource_pb2.Resource, _Mapping]] = ..., email: _Optional[str] = ..., username: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., full_name: _Optional[str] = ..., display_name: _Optional[str] = ..., title: _Optional[str] = ..., status: _Optional[str] = ..., manager_email: _Optional[str] = ..., profiles: _Optional[_Iterable[_Union[Profile, _Mapping]]] = ..., memberships: _Optional[_Iterable[_Union[Membership, _Mapping]]] = ..., properties: _Optional[_Union[_properties_pb2.Properties, _Mapping]] = ..., timestamps: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., event: _Optional[_Union[_event_pb2.Event, _Mapping]] = ...) -> None: ...

class Membership(_message.Message):
    __slots__ = ("group_urn", "role")
    GROUP_URN_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    group_urn: str
    role: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, group_urn: _Optional[str] = ..., role: _Optional[_Iterable[str]] = ...) -> None: ...

class Profile(_message.Message):
    __slots__ = ("id", "platform", "url")
    ID_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    platform: str
    url: str
    def __init__(self, id: _Optional[str] = ..., platform: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...
