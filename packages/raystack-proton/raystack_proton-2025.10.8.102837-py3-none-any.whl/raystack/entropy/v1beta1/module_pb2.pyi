import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Module(_message.Message):
    __slots__ = ("urn", "name", "project", "created_at", "updated_at", "configs")
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    urn: str
    name: str
    project: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    configs: _struct_pb2.Value
    def __init__(self, urn: _Optional[str] = ..., name: _Optional[str] = ..., project: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., configs: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...

class ListModulesRequest(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: str
    def __init__(self, project: _Optional[str] = ...) -> None: ...

class ListModulesResponse(_message.Message):
    __slots__ = ("modules",)
    MODULES_FIELD_NUMBER: _ClassVar[int]
    modules: _containers.RepeatedCompositeFieldContainer[Module]
    def __init__(self, modules: _Optional[_Iterable[_Union[Module, _Mapping]]] = ...) -> None: ...

class GetModuleRequest(_message.Message):
    __slots__ = ("urn",)
    URN_FIELD_NUMBER: _ClassVar[int]
    urn: str
    def __init__(self, urn: _Optional[str] = ...) -> None: ...

class GetModuleResponse(_message.Message):
    __slots__ = ("module",)
    MODULE_FIELD_NUMBER: _ClassVar[int]
    module: Module
    def __init__(self, module: _Optional[_Union[Module, _Mapping]] = ...) -> None: ...

class CreateModuleRequest(_message.Message):
    __slots__ = ("module",)
    MODULE_FIELD_NUMBER: _ClassVar[int]
    module: Module
    def __init__(self, module: _Optional[_Union[Module, _Mapping]] = ...) -> None: ...

class CreateModuleResponse(_message.Message):
    __slots__ = ("module",)
    MODULE_FIELD_NUMBER: _ClassVar[int]
    module: Module
    def __init__(self, module: _Optional[_Union[Module, _Mapping]] = ...) -> None: ...

class UpdateModuleRequest(_message.Message):
    __slots__ = ("urn", "configs")
    URN_FIELD_NUMBER: _ClassVar[int]
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    urn: str
    configs: _struct_pb2.Value
    def __init__(self, urn: _Optional[str] = ..., configs: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...

class UpdateModuleResponse(_message.Message):
    __slots__ = ("module",)
    MODULE_FIELD_NUMBER: _ClassVar[int]
    module: Module
    def __init__(self, module: _Optional[_Union[Module, _Mapping]] = ...) -> None: ...

class DeleteModuleRequest(_message.Message):
    __slots__ = ("urn",)
    URN_FIELD_NUMBER: _ClassVar[int]
    urn: str
    def __init__(self, urn: _Optional[str] = ...) -> None: ...

class DeleteModuleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
