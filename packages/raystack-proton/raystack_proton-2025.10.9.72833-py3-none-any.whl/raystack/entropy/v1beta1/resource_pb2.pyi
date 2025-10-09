import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceDependency(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ResourceSpec(_message.Message):
    __slots__ = ("configs", "dependencies")
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    configs: _struct_pb2.Value
    dependencies: _containers.RepeatedCompositeFieldContainer[ResourceDependency]
    def __init__(self, configs: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., dependencies: _Optional[_Iterable[_Union[ResourceDependency, _Mapping]]] = ...) -> None: ...

class ListString(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class LogOptions(_message.Message):
    __slots__ = ("filters",)
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ListString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ListString, _Mapping]] = ...) -> None: ...
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.MessageMap[str, ListString]
    def __init__(self, filters: _Optional[_Mapping[str, ListString]] = ...) -> None: ...

class ResourceState(_message.Message):
    __slots__ = ("status", "output", "module_data", "log_options")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[ResourceState.Status]
        STATUS_PENDING: _ClassVar[ResourceState.Status]
        STATUS_ERROR: _ClassVar[ResourceState.Status]
        STATUS_DELETED: _ClassVar[ResourceState.Status]
        STATUS_COMPLETED: _ClassVar[ResourceState.Status]
    STATUS_UNSPECIFIED: ResourceState.Status
    STATUS_PENDING: ResourceState.Status
    STATUS_ERROR: ResourceState.Status
    STATUS_DELETED: ResourceState.Status
    STATUS_COMPLETED: ResourceState.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    MODULE_DATA_FIELD_NUMBER: _ClassVar[int]
    LOG_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    status: ResourceState.Status
    output: _struct_pb2.Value
    module_data: bytes
    log_options: LogOptions
    def __init__(self, status: _Optional[_Union[ResourceState.Status, str]] = ..., output: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., module_data: _Optional[bytes] = ..., log_options: _Optional[_Union[LogOptions, _Mapping]] = ...) -> None: ...

class Resource(_message.Message):
    __slots__ = ("urn", "kind", "name", "project", "labels", "created_at", "updated_at", "spec", "state")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URN_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    urn: str
    kind: str
    name: str
    project: str
    labels: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    spec: ResourceSpec
    state: ResourceState
    def __init__(self, urn: _Optional[str] = ..., kind: _Optional[str] = ..., name: _Optional[str] = ..., project: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., spec: _Optional[_Union[ResourceSpec, _Mapping]] = ..., state: _Optional[_Union[ResourceState, _Mapping]] = ...) -> None: ...

class ListResourcesRequest(_message.Message):
    __slots__ = ("project", "kind")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    project: str
    kind: str
    def __init__(self, project: _Optional[str] = ..., kind: _Optional[str] = ...) -> None: ...

class ListResourcesResponse(_message.Message):
    __slots__ = ("resources",)
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    resources: _containers.RepeatedCompositeFieldContainer[Resource]
    def __init__(self, resources: _Optional[_Iterable[_Union[Resource, _Mapping]]] = ...) -> None: ...

class GetResourceRequest(_message.Message):
    __slots__ = ("urn",)
    URN_FIELD_NUMBER: _ClassVar[int]
    urn: str
    def __init__(self, urn: _Optional[str] = ...) -> None: ...

class GetResourceResponse(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: Resource
    def __init__(self, resource: _Optional[_Union[Resource, _Mapping]] = ...) -> None: ...

class CreateResourceRequest(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: Resource
    def __init__(self, resource: _Optional[_Union[Resource, _Mapping]] = ...) -> None: ...

class CreateResourceResponse(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: Resource
    def __init__(self, resource: _Optional[_Union[Resource, _Mapping]] = ...) -> None: ...

class UpdateResourceRequest(_message.Message):
    __slots__ = ("urn", "new_spec", "labels")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URN_FIELD_NUMBER: _ClassVar[int]
    NEW_SPEC_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    urn: str
    new_spec: ResourceSpec
    labels: _containers.ScalarMap[str, str]
    def __init__(self, urn: _Optional[str] = ..., new_spec: _Optional[_Union[ResourceSpec, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UpdateResourceResponse(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: Resource
    def __init__(self, resource: _Optional[_Union[Resource, _Mapping]] = ...) -> None: ...

class DeleteResourceRequest(_message.Message):
    __slots__ = ("urn",)
    URN_FIELD_NUMBER: _ClassVar[int]
    urn: str
    def __init__(self, urn: _Optional[str] = ...) -> None: ...

class DeleteResourceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ApplyActionRequest(_message.Message):
    __slots__ = ("urn", "action", "params", "labels")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URN_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    urn: str
    action: str
    params: _struct_pb2.Value
    labels: _containers.ScalarMap[str, str]
    def __init__(self, urn: _Optional[str] = ..., action: _Optional[str] = ..., params: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ApplyActionResponse(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: Resource
    def __init__(self, resource: _Optional[_Union[Resource, _Mapping]] = ...) -> None: ...

class LogChunk(_message.Message):
    __slots__ = ("data", "labels")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    labels: _containers.ScalarMap[str, str]
    def __init__(self, data: _Optional[bytes] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetLogRequest(_message.Message):
    __slots__ = ("urn", "filter")
    class FilterEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URN_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    urn: str
    filter: _containers.ScalarMap[str, str]
    def __init__(self, urn: _Optional[str] = ..., filter: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetLogResponse(_message.Message):
    __slots__ = ("chunk",)
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    chunk: LogChunk
    def __init__(self, chunk: _Optional[_Union[LogChunk, _Mapping]] = ...) -> None: ...

class ResourceRevision(_message.Message):
    __slots__ = ("id", "urn", "labels", "created_at", "spec", "reason")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    id: str
    urn: str
    labels: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    spec: ResourceSpec
    reason: str
    def __init__(self, id: _Optional[str] = ..., urn: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., spec: _Optional[_Union[ResourceSpec, _Mapping]] = ..., reason: _Optional[str] = ...) -> None: ...

class GetResourceRevisionsRequest(_message.Message):
    __slots__ = ("urn",)
    URN_FIELD_NUMBER: _ClassVar[int]
    urn: str
    def __init__(self, urn: _Optional[str] = ...) -> None: ...

class GetResourceRevisionsResponse(_message.Message):
    __slots__ = ("revisions",)
    REVISIONS_FIELD_NUMBER: _ClassVar[int]
    revisions: _containers.RepeatedCompositeFieldContainer[ResourceRevision]
    def __init__(self, revisions: _Optional[_Iterable[_Union[ResourceRevision, _Mapping]]] = ...) -> None: ...
