from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Ownership(_message.Message):
    __slots__ = ("owners",)
    OWNERS_FIELD_NUMBER: _ClassVar[int]
    owners: _containers.RepeatedCompositeFieldContainer[Owner]
    def __init__(self, owners: _Optional[_Iterable[_Union[Owner, _Mapping]]] = ...) -> None: ...

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
