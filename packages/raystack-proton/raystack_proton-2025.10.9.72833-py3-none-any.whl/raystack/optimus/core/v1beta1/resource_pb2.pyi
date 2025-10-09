from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from raystack.optimus.core.v1beta1 import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeployResourceSpecificationRequest(_message.Message):
    __slots__ = ("project_name", "datastore_name", "resources", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    datastore_name: str
    resources: _containers.RepeatedCompositeFieldContainer[ResourceSpecification]
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., resources: _Optional[_Iterable[_Union[ResourceSpecification, _Mapping]]] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class DeployResourceSpecificationResponse(_message.Message):
    __slots__ = ("log_status",)
    LOG_STATUS_FIELD_NUMBER: _ClassVar[int]
    log_status: _status_pb2.Log
    def __init__(self, log_status: _Optional[_Union[_status_pb2.Log, _Mapping]] = ...) -> None: ...

class ListResourceSpecificationRequest(_message.Message):
    __slots__ = ("project_name", "datastore_name", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    datastore_name: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class ListResourceSpecificationResponse(_message.Message):
    __slots__ = ("resources",)
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    resources: _containers.RepeatedCompositeFieldContainer[ResourceSpecification]
    def __init__(self, resources: _Optional[_Iterable[_Union[ResourceSpecification, _Mapping]]] = ...) -> None: ...

class CreateResourceRequest(_message.Message):
    __slots__ = ("project_name", "datastore_name", "resource", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    datastore_name: str
    resource: ResourceSpecification
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., resource: _Optional[_Union[ResourceSpecification, _Mapping]] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class CreateResourceResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...

class ReadResourceRequest(_message.Message):
    __slots__ = ("project_name", "datastore_name", "resource_name", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    datastore_name: str
    resource_name: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., resource_name: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class ReadResourceResponse(_message.Message):
    __slots__ = ("success", "message", "resource")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    resource: ResourceSpecification
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ..., resource: _Optional[_Union[ResourceSpecification, _Mapping]] = ...) -> None: ...

class UpdateResourceRequest(_message.Message):
    __slots__ = ("project_name", "datastore_name", "resource", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    datastore_name: str
    resource: ResourceSpecification
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., resource: _Optional[_Union[ResourceSpecification, _Mapping]] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class UpdateResourceResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...

class ResourceSpecification(_message.Message):
    __slots__ = ("version", "name", "type", "spec", "assets", "labels")
    class AssetsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    version: int
    name: str
    type: str
    spec: _struct_pb2.Struct
    assets: _containers.ScalarMap[str, str]
    labels: _containers.ScalarMap[str, str]
    def __init__(self, version: _Optional[int] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., spec: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., assets: _Optional[_Mapping[str, str]] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ChangeResourceNamespaceRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "datastore_name", "resource_name", "new_namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    NEW_NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    datastore_name: str
    resource_name: str
    new_namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., resource_name: _Optional[str] = ..., new_namespace_name: _Optional[str] = ...) -> None: ...

class ChangeResourceNamespaceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ApplyResourcesRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "datastore_name", "resource_names")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAMES_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    datastore_name: str
    resource_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., resource_names: _Optional[_Iterable[str]] = ...) -> None: ...

class ApplyResourcesResponse(_message.Message):
    __slots__ = ("statuses",)
    class ResourceStatus(_message.Message):
        __slots__ = ("resource_name", "status", "reason")
        RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        REASON_FIELD_NUMBER: _ClassVar[int]
        resource_name: str
        status: str
        reason: str
        def __init__(self, resource_name: _Optional[str] = ..., status: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    statuses: _containers.RepeatedCompositeFieldContainer[ApplyResourcesResponse.ResourceStatus]
    def __init__(self, statuses: _Optional[_Iterable[_Union[ApplyResourcesResponse.ResourceStatus, _Mapping]]] = ...) -> None: ...
