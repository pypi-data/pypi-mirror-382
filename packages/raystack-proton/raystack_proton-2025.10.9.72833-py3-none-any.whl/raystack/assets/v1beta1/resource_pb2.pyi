from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Resource(_message.Message):
    __slots__ = ("urn", "name", "service", "type", "url", "description")
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    urn: str
    name: str
    service: str
    type: str
    url: str
    description: str
    def __init__(self, urn: _Optional[str] = ..., name: _Optional[str] = ..., service: _Optional[str] = ..., type: _Optional[str] = ..., url: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
