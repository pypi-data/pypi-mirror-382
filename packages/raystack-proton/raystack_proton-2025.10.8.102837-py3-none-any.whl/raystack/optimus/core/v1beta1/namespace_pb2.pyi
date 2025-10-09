from google.api import annotations_pb2 as _annotations_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RegisterProjectNamespaceRequest(_message.Message):
    __slots__ = ("project_name", "namespace")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace: NamespaceSpecification
    def __init__(self, project_name: _Optional[str] = ..., namespace: _Optional[_Union[NamespaceSpecification, _Mapping]] = ...) -> None: ...

class RegisterProjectNamespaceResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...

class ListProjectNamespacesRequest(_message.Message):
    __slots__ = ("project_name",)
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    def __init__(self, project_name: _Optional[str] = ...) -> None: ...

class ListProjectNamespacesResponse(_message.Message):
    __slots__ = ("namespaces",)
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    namespaces: _containers.RepeatedCompositeFieldContainer[NamespaceSpecification]
    def __init__(self, namespaces: _Optional[_Iterable[_Union[NamespaceSpecification, _Mapping]]] = ...) -> None: ...

class GetNamespaceRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class GetNamespaceResponse(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: NamespaceSpecification
    def __init__(self, namespace: _Optional[_Union[NamespaceSpecification, _Mapping]] = ...) -> None: ...

class NamespaceSpecification(_message.Message):
    __slots__ = ("name", "config")
    class ConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    config: _containers.ScalarMap[str, str]
    def __init__(self, name: _Optional[str] = ..., config: _Optional[_Mapping[str, str]] = ...) -> None: ...
