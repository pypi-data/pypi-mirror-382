import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IgnoredResource(_message.Message):
    __slots__ = ("name", "reason")
    NAME_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    name: str
    reason: str
    def __init__(self, name: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class CreateBackupRequest(_message.Message):
    __slots__ = ("project_name", "datastore_name", "namespace_name", "description", "config", "resource_names")
    class ConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAMES_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    datastore_name: str
    namespace_name: str
    description: str
    config: _containers.ScalarMap[str, str]
    resource_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., description: _Optional[str] = ..., config: _Optional[_Mapping[str, str]] = ..., resource_names: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateBackupResponse(_message.Message):
    __slots__ = ("resource_names", "ignored_resources", "backup_id")
    RESOURCE_NAMES_FIELD_NUMBER: _ClassVar[int]
    IGNORED_RESOURCES_FIELD_NUMBER: _ClassVar[int]
    BACKUP_ID_FIELD_NUMBER: _ClassVar[int]
    resource_names: _containers.RepeatedScalarFieldContainer[str]
    ignored_resources: _containers.RepeatedCompositeFieldContainer[IgnoredResource]
    backup_id: str
    def __init__(self, resource_names: _Optional[_Iterable[str]] = ..., ignored_resources: _Optional[_Iterable[_Union[IgnoredResource, _Mapping]]] = ..., backup_id: _Optional[str] = ...) -> None: ...

class ListBackupsRequest(_message.Message):
    __slots__ = ("project_name", "datastore_name", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    datastore_name: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class ListBackupsResponse(_message.Message):
    __slots__ = ("backups",)
    BACKUPS_FIELD_NUMBER: _ClassVar[int]
    backups: _containers.RepeatedCompositeFieldContainer[BackupSpec]
    def __init__(self, backups: _Optional[_Iterable[_Union[BackupSpec, _Mapping]]] = ...) -> None: ...

class BackupSpec(_message.Message):
    __slots__ = ("id", "created_at", "description", "config", "resource_names")
    class ConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAMES_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    description: str
    config: _containers.ScalarMap[str, str]
    resource_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., description: _Optional[str] = ..., config: _Optional[_Mapping[str, str]] = ..., resource_names: _Optional[_Iterable[str]] = ...) -> None: ...

class GetBackupRequest(_message.Message):
    __slots__ = ("project_name", "datastore_name", "namespace_name", "id")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    datastore_name: str
    namespace_name: str
    id: str
    def __init__(self, project_name: _Optional[str] = ..., datastore_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class GetBackupResponse(_message.Message):
    __slots__ = ("spec",)
    SPEC_FIELD_NUMBER: _ClassVar[int]
    spec: BackupSpec
    def __init__(self, spec: _Optional[_Union[BackupSpec, _Mapping]] = ...) -> None: ...
