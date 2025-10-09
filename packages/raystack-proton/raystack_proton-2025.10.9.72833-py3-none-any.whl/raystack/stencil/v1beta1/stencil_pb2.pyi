import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Namespace(_message.Message):
    __slots__ = ("id", "format", "compatibility", "description", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    format: Schema.Format
    compatibility: Schema.Compatibility
    description: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., format: _Optional[_Union[Schema.Format, str]] = ..., compatibility: _Optional[_Union[Schema.Compatibility, str]] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Schema(_message.Message):
    __slots__ = ("name", "format", "authority", "compatibility", "created_at", "updated_at")
    class Format(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FORMAT_UNSPECIFIED: _ClassVar[Schema.Format]
        FORMAT_PROTOBUF: _ClassVar[Schema.Format]
        FORMAT_AVRO: _ClassVar[Schema.Format]
        FORMAT_JSON: _ClassVar[Schema.Format]
    FORMAT_UNSPECIFIED: Schema.Format
    FORMAT_PROTOBUF: Schema.Format
    FORMAT_AVRO: Schema.Format
    FORMAT_JSON: Schema.Format
    class Compatibility(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COMPATIBILITY_UNSPECIFIED: _ClassVar[Schema.Compatibility]
        COMPATIBILITY_BACKWARD: _ClassVar[Schema.Compatibility]
        COMPATIBILITY_BACKWARD_TRANSITIVE: _ClassVar[Schema.Compatibility]
        COMPATIBILITY_FORWARD: _ClassVar[Schema.Compatibility]
        COMPATIBILITY_FORWARD_TRANSITIVE: _ClassVar[Schema.Compatibility]
        COMPATIBILITY_FULL: _ClassVar[Schema.Compatibility]
        COMPATIBILITY_FULL_TRANSITIVE: _ClassVar[Schema.Compatibility]
    COMPATIBILITY_UNSPECIFIED: Schema.Compatibility
    COMPATIBILITY_BACKWARD: Schema.Compatibility
    COMPATIBILITY_BACKWARD_TRANSITIVE: Schema.Compatibility
    COMPATIBILITY_FORWARD: Schema.Compatibility
    COMPATIBILITY_FORWARD_TRANSITIVE: Schema.Compatibility
    COMPATIBILITY_FULL: Schema.Compatibility
    COMPATIBILITY_FULL_TRANSITIVE: Schema.Compatibility
    NAME_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    AUTHORITY_FIELD_NUMBER: _ClassVar[int]
    COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    format: Schema.Format
    authority: str
    compatibility: Schema.Compatibility
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., format: _Optional[_Union[Schema.Format, str]] = ..., authority: _Optional[str] = ..., compatibility: _Optional[_Union[Schema.Compatibility, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListNamespacesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNamespacesResponse(_message.Message):
    __slots__ = ("namespaces",)
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    namespaces: _containers.RepeatedCompositeFieldContainer[Namespace]
    def __init__(self, namespaces: _Optional[_Iterable[_Union[Namespace, _Mapping]]] = ...) -> None: ...

class GetNamespaceRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetNamespaceResponse(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: Namespace
    def __init__(self, namespace: _Optional[_Union[Namespace, _Mapping]] = ...) -> None: ...

class CreateNamespaceRequest(_message.Message):
    __slots__ = ("id", "format", "compatibility", "description")
    ID_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    format: Schema.Format
    compatibility: Schema.Compatibility
    description: str
    def __init__(self, id: _Optional[str] = ..., format: _Optional[_Union[Schema.Format, str]] = ..., compatibility: _Optional[_Union[Schema.Compatibility, str]] = ..., description: _Optional[str] = ...) -> None: ...

class CreateNamespaceResponse(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: Namespace
    def __init__(self, namespace: _Optional[_Union[Namespace, _Mapping]] = ...) -> None: ...

class UpdateNamespaceRequest(_message.Message):
    __slots__ = ("id", "format", "compatibility", "description")
    ID_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    format: Schema.Format
    compatibility: Schema.Compatibility
    description: str
    def __init__(self, id: _Optional[str] = ..., format: _Optional[_Union[Schema.Format, str]] = ..., compatibility: _Optional[_Union[Schema.Compatibility, str]] = ..., description: _Optional[str] = ...) -> None: ...

class UpdateNamespaceResponse(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: Namespace
    def __init__(self, namespace: _Optional[_Union[Namespace, _Mapping]] = ...) -> None: ...

class DeleteNamespaceRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteNamespaceResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class ListSchemasRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListSchemasResponse(_message.Message):
    __slots__ = ("schemas",)
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    schemas: _containers.RepeatedCompositeFieldContainer[Schema]
    def __init__(self, schemas: _Optional[_Iterable[_Union[Schema, _Mapping]]] = ...) -> None: ...

class GetLatestSchemaRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ...) -> None: ...

class GetLatestSchemaResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...

class CreateSchemaRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id", "data", "format", "compatibility")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    data: bytes
    format: Schema.Format
    compatibility: Schema.Compatibility
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ..., data: _Optional[bytes] = ..., format: _Optional[_Union[Schema.Format, str]] = ..., compatibility: _Optional[_Union[Schema.Compatibility, str]] = ...) -> None: ...

class CreateSchemaResponse(_message.Message):
    __slots__ = ("version", "id", "location")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    version: int
    id: str
    location: str
    def __init__(self, version: _Optional[int] = ..., id: _Optional[str] = ..., location: _Optional[str] = ...) -> None: ...

class CheckCompatibilityRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id", "data", "compatibility")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    data: bytes
    compatibility: Schema.Compatibility
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ..., data: _Optional[bytes] = ..., compatibility: _Optional[_Union[Schema.Compatibility, str]] = ...) -> None: ...

class CheckCompatibilityResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetSchemaMetadataRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ...) -> None: ...

class GetSchemaMetadataResponse(_message.Message):
    __slots__ = ("format", "compatibility", "authority", "name", "created_at", "updated_at")
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    AUTHORITY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    format: Schema.Format
    compatibility: Schema.Compatibility
    authority: str
    name: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, format: _Optional[_Union[Schema.Format, str]] = ..., compatibility: _Optional[_Union[Schema.Compatibility, str]] = ..., authority: _Optional[str] = ..., name: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UpdateSchemaMetadataRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id", "compatibility")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    compatibility: Schema.Compatibility
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ..., compatibility: _Optional[_Union[Schema.Compatibility, str]] = ...) -> None: ...

class UpdateSchemaMetadataResponse(_message.Message):
    __slots__ = ("format", "compatibility", "authority")
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    AUTHORITY_FIELD_NUMBER: _ClassVar[int]
    format: Schema.Format
    compatibility: Schema.Compatibility
    authority: str
    def __init__(self, format: _Optional[_Union[Schema.Format, str]] = ..., compatibility: _Optional[_Union[Schema.Compatibility, str]] = ..., authority: _Optional[str] = ...) -> None: ...

class DeleteSchemaRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ...) -> None: ...

class DeleteSchemaResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class ListVersionsRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ...) -> None: ...

class ListVersionsResponse(_message.Message):
    __slots__ = ("versions",)
    VERSIONS_FIELD_NUMBER: _ClassVar[int]
    versions: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, versions: _Optional[_Iterable[int]] = ...) -> None: ...

class GetSchemaRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id", "version_id")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    version_id: int
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ..., version_id: _Optional[int] = ...) -> None: ...

class GetSchemaResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...

class DeleteVersionRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id", "version_id")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    version_id: int
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ..., version_id: _Optional[int] = ...) -> None: ...

class DeleteVersionResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class SearchRequest(_message.Message):
    __slots__ = ("namespace_id", "schema_id", "query", "history", "version_id")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    query: str
    history: bool
    version_id: int
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ..., query: _Optional[str] = ..., history: _Optional[bool] = ..., version_id: _Optional[int] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("hits", "meta")
    HITS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    hits: _containers.RepeatedCompositeFieldContainer[SearchHits]
    meta: SearchMeta
    def __init__(self, hits: _Optional[_Iterable[_Union[SearchHits, _Mapping]]] = ..., meta: _Optional[_Union[SearchMeta, _Mapping]] = ...) -> None: ...

class SearchHits(_message.Message):
    __slots__ = ("namespace_id", "schema_id", "version_id", "fields", "types", "path")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    namespace_id: str
    schema_id: str
    version_id: int
    fields: _containers.RepeatedScalarFieldContainer[str]
    types: _containers.RepeatedScalarFieldContainer[str]
    path: str
    def __init__(self, namespace_id: _Optional[str] = ..., schema_id: _Optional[str] = ..., version_id: _Optional[int] = ..., fields: _Optional[_Iterable[str]] = ..., types: _Optional[_Iterable[str]] = ..., path: _Optional[str] = ...) -> None: ...

class SearchMeta(_message.Message):
    __slots__ = ("total",)
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    total: int
    def __init__(self, total: _Optional[int] = ...) -> None: ...
