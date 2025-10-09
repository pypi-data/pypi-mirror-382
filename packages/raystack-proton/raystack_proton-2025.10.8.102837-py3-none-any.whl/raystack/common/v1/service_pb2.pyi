import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetVersionRequest(_message.Message):
    __slots__ = ("client",)
    CLIENT_FIELD_NUMBER: _ClassVar[int]
    client: Version
    def __init__(self, client: _Optional[_Union[Version, _Mapping]] = ...) -> None: ...

class GetVersionResponse(_message.Message):
    __slots__ = ("server",)
    SERVER_FIELD_NUMBER: _ClassVar[int]
    server: Version
    def __init__(self, server: _Optional[_Union[Version, _Mapping]] = ...) -> None: ...

class Version(_message.Message):
    __slots__ = ("version", "commit", "build_time", "lang_version", "os", "architecture")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    COMMIT_FIELD_NUMBER: _ClassVar[int]
    BUILD_TIME_FIELD_NUMBER: _ClassVar[int]
    LANG_VERSION_FIELD_NUMBER: _ClassVar[int]
    OS_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    version: str
    commit: str
    build_time: _timestamp_pb2.Timestamp
    lang_version: str
    os: str
    architecture: str
    def __init__(self, version: _Optional[str] = ..., commit: _Optional[str] = ..., build_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., lang_version: _Optional[str] = ..., os: _Optional[str] = ..., architecture: _Optional[str] = ...) -> None: ...
