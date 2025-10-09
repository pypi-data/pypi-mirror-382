from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Group(_message.Message):
    __slots__ = ("email", "members", "attributes")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    email: str
    members: _containers.RepeatedCompositeFieldContainer[Member]
    attributes: _struct_pb2.Struct
    def __init__(self, email: _Optional[str] = ..., members: _Optional[_Iterable[_Union[Member, _Mapping]]] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class Member(_message.Message):
    __slots__ = ("urn", "role")
    URN_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    urn: str
    role: str
    def __init__(self, urn: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...
