import datetime

from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("id", "name", "title", "email", "metadata", "created_at", "updated_at", "state", "avatar")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    title: str
    email: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    state: str
    avatar: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., email: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[str] = ..., avatar: _Optional[str] = ...) -> None: ...

class ServiceUser(_message.Message):
    __slots__ = ("id", "title", "metadata", "created_at", "updated_at", "state", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    state: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class Group(_message.Message):
    __slots__ = ("id", "name", "title", "org_id", "metadata", "created_at", "updated_at", "users", "members_count")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_COUNT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    title: str
    org_id: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    users: _containers.RepeatedCompositeFieldContainer[User]
    members_count: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., org_id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., users: _Optional[_Iterable[_Union[User, _Mapping]]] = ..., members_count: _Optional[int] = ...) -> None: ...

class Role(_message.Message):
    __slots__ = ("id", "name", "permissions", "title", "metadata", "created_at", "updated_at", "org_id", "state", "scopes")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    permissions: _containers.RepeatedScalarFieldContainer[str]
    title: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    org_id: str
    state: str
    scopes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., permissions: _Optional[_Iterable[str]] = ..., title: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., org_id: _Optional[str] = ..., state: _Optional[str] = ..., scopes: _Optional[_Iterable[str]] = ...) -> None: ...

class Organization(_message.Message):
    __slots__ = ("id", "name", "title", "metadata", "created_at", "updated_at", "state", "avatar")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    title: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    state: str
    avatar: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[str] = ..., avatar: _Optional[str] = ...) -> None: ...

class OrganizationKyc(_message.Message):
    __slots__ = ("org_id", "status", "link", "created_at", "updated_at")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    status: bool
    link: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, org_id: _Optional[str] = ..., status: _Optional[bool] = ..., link: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Project(_message.Message):
    __slots__ = ("id", "name", "title", "org_id", "metadata", "created_at", "updated_at", "members_count")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_COUNT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    title: str
    org_id: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    members_count: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., org_id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., members_count: _Optional[int] = ...) -> None: ...

class Domain(_message.Message):
    __slots__ = ("id", "name", "org_id", "token", "state", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    org_id: str
    token: str
    state: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., org_id: _Optional[str] = ..., token: _Optional[str] = ..., state: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Policy(_message.Message):
    __slots__ = ("id", "title", "created_at", "updated_at", "role_id", "resource", "principal", "metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    role_id: str
    resource: str
    principal: str
    metadata: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., role_id: _Optional[str] = ..., resource: _Optional[str] = ..., principal: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class Relation(_message.Message):
    __slots__ = ("id", "created_at", "updated_at", "subject_sub_relation", "relation", "object", "subject")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_SUB_RELATION_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    subject_sub_relation: str
    relation: str
    object: str
    subject: str
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., subject_sub_relation: _Optional[str] = ..., relation: _Optional[str] = ..., object: _Optional[str] = ..., subject: _Optional[str] = ...) -> None: ...

class Permission(_message.Message):
    __slots__ = ("id", "name", "title", "created_at", "updated_at", "namespace", "metadata", "key")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    title: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    namespace: str
    metadata: _struct_pb2.Struct
    key: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., namespace: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., key: _Optional[str] = ...) -> None: ...

class Namespace(_message.Message):
    __slots__ = ("id", "name", "metadata", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Resource(_message.Message):
    __slots__ = ("id", "name", "created_at", "updated_at", "urn", "project_id", "namespace", "principal", "metadata", "title")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    urn: str
    project_id: str
    namespace: str
    principal: str
    metadata: _struct_pb2.Struct
    title: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., urn: _Optional[str] = ..., project_id: _Optional[str] = ..., namespace: _Optional[str] = ..., principal: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., title: _Optional[str] = ...) -> None: ...

class MetaSchema(_message.Message):
    __slots__ = ("id", "name", "schema", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    schema: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., schema: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Invitation(_message.Message):
    __slots__ = ("id", "user_id", "org_id", "group_ids", "metadata", "created_at", "expires_at", "role_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    org_id: str
    group_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    expires_at: _timestamp_pb2.Timestamp
    role_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ..., org_id: _Optional[str] = ..., group_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., role_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ServiceUserJWK(_message.Message):
    __slots__ = ("id", "title", "principal_id", "public_key", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    principal_id: str
    public_key: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., principal_id: _Optional[str] = ..., public_key: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class KeyCredential(_message.Message):
    __slots__ = ("type", "kid", "principal_id", "private_key")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    KID_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    type: str
    kid: str
    principal_id: str
    private_key: str
    def __init__(self, type: _Optional[str] = ..., kid: _Optional[str] = ..., principal_id: _Optional[str] = ..., private_key: _Optional[str] = ...) -> None: ...

class SecretCredential(_message.Message):
    __slots__ = ("id", "title", "secret", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    secret: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., secret: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ServiceUserToken(_message.Message):
    __slots__ = ("id", "title", "token", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    token: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., token: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class JSONWebKey(_message.Message):
    __slots__ = ("kty", "alg", "use", "kid", "n", "e", "x", "y", "crv")
    KTY_FIELD_NUMBER: _ClassVar[int]
    ALG_FIELD_NUMBER: _ClassVar[int]
    USE_FIELD_NUMBER: _ClassVar[int]
    KID_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    E_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    CRV_FIELD_NUMBER: _ClassVar[int]
    kty: str
    alg: str
    use: str
    kid: str
    n: str
    e: str
    x: str
    y: str
    crv: str
    def __init__(self, kty: _Optional[str] = ..., alg: _Optional[str] = ..., use: _Optional[str] = ..., kid: _Optional[str] = ..., n: _Optional[str] = ..., e: _Optional[str] = ..., x: _Optional[str] = ..., y: _Optional[str] = ..., crv: _Optional[str] = ...) -> None: ...

class AuditLogActor(_message.Message):
    __slots__ = ("id", "type", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    name: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class AuditLogTarget(_message.Message):
    __slots__ = ("id", "type", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    name: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class AuditLog(_message.Message):
    __slots__ = ("id", "source", "action", "actor", "target", "context", "created_at")
    class ContextEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    source: str
    action: str
    actor: AuditLogActor
    target: AuditLogTarget
    context: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., source: _Optional[str] = ..., action: _Optional[str] = ..., actor: _Optional[_Union[AuditLogActor, _Mapping]] = ..., target: _Optional[_Union[AuditLogTarget, _Mapping]] = ..., context: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PreferenceTrait(_message.Message):
    __slots__ = ("resource_type", "name", "title", "description", "long_description", "heading", "sub_heading", "breadcrumb", "default", "input_hints", "text", "textarea", "select", "combobox", "checkbox", "multiselect", "number")
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LONG_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    HEADING_FIELD_NUMBER: _ClassVar[int]
    SUB_HEADING_FIELD_NUMBER: _ClassVar[int]
    BREADCRUMB_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FIELD_NUMBER: _ClassVar[int]
    INPUT_HINTS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TEXTAREA_FIELD_NUMBER: _ClassVar[int]
    SELECT_FIELD_NUMBER: _ClassVar[int]
    COMBOBOX_FIELD_NUMBER: _ClassVar[int]
    CHECKBOX_FIELD_NUMBER: _ClassVar[int]
    MULTISELECT_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    resource_type: str
    name: str
    title: str
    description: str
    long_description: str
    heading: str
    sub_heading: str
    breadcrumb: str
    default: str
    input_hints: str
    text: str
    textarea: str
    select: str
    combobox: str
    checkbox: str
    multiselect: str
    number: str
    def __init__(self, resource_type: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., long_description: _Optional[str] = ..., heading: _Optional[str] = ..., sub_heading: _Optional[str] = ..., breadcrumb: _Optional[str] = ..., default: _Optional[str] = ..., input_hints: _Optional[str] = ..., text: _Optional[str] = ..., textarea: _Optional[str] = ..., select: _Optional[str] = ..., combobox: _Optional[str] = ..., checkbox: _Optional[str] = ..., multiselect: _Optional[str] = ..., number: _Optional[str] = ...) -> None: ...

class Preference(_message.Message):
    __slots__ = ("id", "name", "value", "resource_id", "resource_type", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    value: str
    resource_id: str
    resource_type: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., value: _Optional[str] = ..., resource_id: _Optional[str] = ..., resource_type: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class BillingAccount(_message.Message):
    __slots__ = ("id", "org_id", "name", "email", "phone", "address", "provider_id", "provider", "currency", "state", "tax_data", "metadata", "created_at", "updated_at", "organization")
    class Address(_message.Message):
        __slots__ = ("line1", "line2", "city", "state", "postal_code", "country")
        LINE1_FIELD_NUMBER: _ClassVar[int]
        LINE2_FIELD_NUMBER: _ClassVar[int]
        CITY_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        POSTAL_CODE_FIELD_NUMBER: _ClassVar[int]
        COUNTRY_FIELD_NUMBER: _ClassVar[int]
        line1: str
        line2: str
        city: str
        state: str
        postal_code: str
        country: str
        def __init__(self, line1: _Optional[str] = ..., line2: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., postal_code: _Optional[str] = ..., country: _Optional[str] = ...) -> None: ...
    class Tax(_message.Message):
        __slots__ = ("type", "id")
        TYPE_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        type: str
        id: str
        def __init__(self, type: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...
    class Balance(_message.Message):
        __slots__ = ("amount", "currency", "updated_at")
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        CURRENCY_FIELD_NUMBER: _ClassVar[int]
        UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
        amount: int
        currency: str
        updated_at: _timestamp_pb2.Timestamp
        def __init__(self, amount: _Optional[int] = ..., currency: _Optional[str] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    TAX_DATA_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    name: str
    email: str
    phone: str
    address: BillingAccount.Address
    provider_id: str
    provider: str
    currency: str
    state: str
    tax_data: _containers.RepeatedCompositeFieldContainer[BillingAccount.Tax]
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    organization: Organization
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., address: _Optional[_Union[BillingAccount.Address, _Mapping]] = ..., provider_id: _Optional[str] = ..., provider: _Optional[str] = ..., currency: _Optional[str] = ..., state: _Optional[str] = ..., tax_data: _Optional[_Iterable[_Union[BillingAccount.Tax, _Mapping]]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., organization: _Optional[_Union[Organization, _Mapping]] = ...) -> None: ...

class BillingAccountDetails(_message.Message):
    __slots__ = ("credit_min", "due_in_days")
    CREDIT_MIN_FIELD_NUMBER: _ClassVar[int]
    DUE_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    credit_min: int
    due_in_days: int
    def __init__(self, credit_min: _Optional[int] = ..., due_in_days: _Optional[int] = ...) -> None: ...

class Subscription(_message.Message):
    __slots__ = ("id", "customer_id", "provider_id", "plan_id", "state", "metadata", "created_at", "updated_at", "canceled_at", "ended_at", "trial_ends_at", "current_period_start_at", "current_period_end_at", "billing_cycle_anchor_at", "phases", "customer", "plan")
    class Phase(_message.Message):
        __slots__ = ("effective_at", "plan_id", "reason")
        EFFECTIVE_AT_FIELD_NUMBER: _ClassVar[int]
        PLAN_ID_FIELD_NUMBER: _ClassVar[int]
        REASON_FIELD_NUMBER: _ClassVar[int]
        effective_at: _timestamp_pb2.Timestamp
        plan_id: str
        reason: str
        def __init__(self, effective_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., plan_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CANCELED_AT_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    TRIAL_ENDS_AT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PERIOD_START_AT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PERIOD_END_AT_FIELD_NUMBER: _ClassVar[int]
    BILLING_CYCLE_ANCHOR_AT_FIELD_NUMBER: _ClassVar[int]
    PHASES_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    PLAN_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer_id: str
    provider_id: str
    plan_id: str
    state: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    canceled_at: _timestamp_pb2.Timestamp
    ended_at: _timestamp_pb2.Timestamp
    trial_ends_at: _timestamp_pb2.Timestamp
    current_period_start_at: _timestamp_pb2.Timestamp
    current_period_end_at: _timestamp_pb2.Timestamp
    billing_cycle_anchor_at: _timestamp_pb2.Timestamp
    phases: _containers.RepeatedCompositeFieldContainer[Subscription.Phase]
    customer: BillingAccount
    plan: Plan
    def __init__(self, id: _Optional[str] = ..., customer_id: _Optional[str] = ..., provider_id: _Optional[str] = ..., plan_id: _Optional[str] = ..., state: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., canceled_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., ended_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., trial_ends_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., current_period_start_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., current_period_end_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., billing_cycle_anchor_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., phases: _Optional[_Iterable[_Union[Subscription.Phase, _Mapping]]] = ..., customer: _Optional[_Union[BillingAccount, _Mapping]] = ..., plan: _Optional[_Union[Plan, _Mapping]] = ...) -> None: ...

class CheckoutSession(_message.Message):
    __slots__ = ("id", "checkout_url", "success_url", "cancel_url", "state", "plan", "product", "metadata", "created_at", "updated_at", "expire_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHECKOUT_URL_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_URL_FIELD_NUMBER: _ClassVar[int]
    CANCEL_URL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PLAN_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    checkout_url: str
    success_url: str
    cancel_url: str
    state: str
    plan: str
    product: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    expire_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., checkout_url: _Optional[str] = ..., success_url: _Optional[str] = ..., cancel_url: _Optional[str] = ..., state: _Optional[str] = ..., plan: _Optional[str] = ..., product: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expire_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Plan(_message.Message):
    __slots__ = ("id", "name", "title", "description", "products", "interval", "on_start_credits", "trial_days", "metadata", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    ON_START_CREDITS_FIELD_NUMBER: _ClassVar[int]
    TRIAL_DAYS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    title: str
    description: str
    products: _containers.RepeatedCompositeFieldContainer[Product]
    interval: str
    on_start_credits: int
    trial_days: int
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ..., interval: _Optional[str] = ..., on_start_credits: _Optional[int] = ..., trial_days: _Optional[int] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Product(_message.Message):
    __slots__ = ("id", "name", "title", "description", "plan_ids", "state", "prices", "behavior", "features", "behavior_config", "metadata", "created_at", "updated_at")
    class BehaviorConfig(_message.Message):
        __slots__ = ("credit_amount", "seat_limit", "min_quantity", "max_quantity")
        CREDIT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
        SEAT_LIMIT_FIELD_NUMBER: _ClassVar[int]
        MIN_QUANTITY_FIELD_NUMBER: _ClassVar[int]
        MAX_QUANTITY_FIELD_NUMBER: _ClassVar[int]
        credit_amount: int
        seat_limit: int
        min_quantity: int
        max_quantity: int
        def __init__(self, credit_amount: _Optional[int] = ..., seat_limit: _Optional[int] = ..., min_quantity: _Optional[int] = ..., max_quantity: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PLAN_IDS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PRICES_FIELD_NUMBER: _ClassVar[int]
    BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    BEHAVIOR_CONFIG_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    title: str
    description: str
    plan_ids: _containers.RepeatedScalarFieldContainer[str]
    state: str
    prices: _containers.RepeatedCompositeFieldContainer[Price]
    behavior: str
    features: _containers.RepeatedCompositeFieldContainer[Feature]
    behavior_config: Product.BehaviorConfig
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., plan_ids: _Optional[_Iterable[str]] = ..., state: _Optional[str] = ..., prices: _Optional[_Iterable[_Union[Price, _Mapping]]] = ..., behavior: _Optional[str] = ..., features: _Optional[_Iterable[_Union[Feature, _Mapping]]] = ..., behavior_config: _Optional[_Union[Product.BehaviorConfig, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Feature(_message.Message):
    __slots__ = ("id", "name", "product_ids", "title", "metadata", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_IDS_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    product_ids: _containers.RepeatedScalarFieldContainer[str]
    title: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., product_ids: _Optional[_Iterable[str]] = ..., title: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Price(_message.Message):
    __slots__ = ("id", "product_id", "provider_id", "name", "interval", "usage_type", "billing_scheme", "state", "currency", "amount", "metered_aggregate", "tier_mode", "metadata", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    USAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    BILLING_SCHEME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    METERED_AGGREGATE_FIELD_NUMBER: _ClassVar[int]
    TIER_MODE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    product_id: str
    provider_id: str
    name: str
    interval: str
    usage_type: str
    billing_scheme: str
    state: str
    currency: str
    amount: int
    metered_aggregate: str
    tier_mode: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., product_id: _Optional[str] = ..., provider_id: _Optional[str] = ..., name: _Optional[str] = ..., interval: _Optional[str] = ..., usage_type: _Optional[str] = ..., billing_scheme: _Optional[str] = ..., state: _Optional[str] = ..., currency: _Optional[str] = ..., amount: _Optional[int] = ..., metered_aggregate: _Optional[str] = ..., tier_mode: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class BillingTransaction(_message.Message):
    __slots__ = ("id", "customer_id", "source", "amount", "type", "description", "user_id", "metadata", "created_at", "updated_at", "user", "customer")
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer_id: str
    source: str
    amount: int
    type: str
    description: str
    user_id: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    user: User
    customer: BillingAccount
    def __init__(self, id: _Optional[str] = ..., customer_id: _Optional[str] = ..., source: _Optional[str] = ..., amount: _Optional[int] = ..., type: _Optional[str] = ..., description: _Optional[str] = ..., user_id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., user: _Optional[_Union[User, _Mapping]] = ..., customer: _Optional[_Union[BillingAccount, _Mapping]] = ...) -> None: ...

class Usage(_message.Message):
    __slots__ = ("id", "customer_id", "source", "description", "type", "amount", "user_id", "metadata", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer_id: str
    source: str
    description: str
    type: str
    amount: int
    user_id: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., customer_id: _Optional[str] = ..., source: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[str] = ..., amount: _Optional[int] = ..., user_id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Invoice(_message.Message):
    __slots__ = ("id", "customer_id", "provider_id", "state", "currency", "amount", "hosted_url", "due_date", "effective_at", "period_start_at", "period_end_at", "metadata", "created_at", "customer")
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    HOSTED_URL_FIELD_NUMBER: _ClassVar[int]
    DUE_DATE_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_AT_FIELD_NUMBER: _ClassVar[int]
    PERIOD_START_AT_FIELD_NUMBER: _ClassVar[int]
    PERIOD_END_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer_id: str
    provider_id: str
    state: str
    currency: str
    amount: int
    hosted_url: str
    due_date: _timestamp_pb2.Timestamp
    effective_at: _timestamp_pb2.Timestamp
    period_start_at: _timestamp_pb2.Timestamp
    period_end_at: _timestamp_pb2.Timestamp
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    customer: BillingAccount
    def __init__(self, id: _Optional[str] = ..., customer_id: _Optional[str] = ..., provider_id: _Optional[str] = ..., state: _Optional[str] = ..., currency: _Optional[str] = ..., amount: _Optional[int] = ..., hosted_url: _Optional[str] = ..., due_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., effective_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., period_start_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., period_end_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., customer: _Optional[_Union[BillingAccount, _Mapping]] = ...) -> None: ...

class PaymentMethod(_message.Message):
    __slots__ = ("id", "customer_id", "provider_id", "type", "card_brand", "card_last4", "card_expiry_month", "card_expiry_year", "metadata", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CARD_BRAND_FIELD_NUMBER: _ClassVar[int]
    CARD_LAST4_FIELD_NUMBER: _ClassVar[int]
    CARD_EXPIRY_MONTH_FIELD_NUMBER: _ClassVar[int]
    CARD_EXPIRY_YEAR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer_id: str
    provider_id: str
    type: str
    card_brand: str
    card_last4: str
    card_expiry_month: int
    card_expiry_year: int
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., customer_id: _Optional[str] = ..., provider_id: _Optional[str] = ..., type: _Optional[str] = ..., card_brand: _Optional[str] = ..., card_last4: _Optional[str] = ..., card_expiry_month: _Optional[int] = ..., card_expiry_year: _Optional[int] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Webhook(_message.Message):
    __slots__ = ("id", "description", "url", "subscribed_events", "headers", "secrets", "state", "metadata", "created_at", "updated_at")
    class Secret(_message.Message):
        __slots__ = ("id", "value")
        ID_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        id: str
        value: str
        def __init__(self, id: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_EVENTS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    description: str
    url: str
    subscribed_events: _containers.RepeatedScalarFieldContainer[str]
    headers: _containers.ScalarMap[str, str]
    secrets: _containers.RepeatedCompositeFieldContainer[Webhook.Secret]
    state: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., description: _Optional[str] = ..., url: _Optional[str] = ..., subscribed_events: _Optional[_Iterable[str]] = ..., headers: _Optional[_Mapping[str, str]] = ..., secrets: _Optional[_Iterable[_Union[Webhook.Secret, _Mapping]]] = ..., state: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class WebhookEvent(_message.Message):
    __slots__ = ("id", "action", "data", "metadata", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    action: str
    data: _struct_pb2.Struct
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., action: _Optional[str] = ..., data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class RoleRequestBody(_message.Message):
    __slots__ = ("name", "permissions", "metadata", "title", "scopes")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    name: str
    permissions: _containers.RepeatedScalarFieldContainer[str]
    metadata: _struct_pb2.Struct
    title: str
    scopes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., permissions: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., title: _Optional[str] = ..., scopes: _Optional[_Iterable[str]] = ...) -> None: ...

class PreferenceRequestBody(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class CheckoutSubscriptionBody(_message.Message):
    __slots__ = ("plan", "skip_trial", "cancel_after_trial", "provider_coupon_id")
    PLAN_FIELD_NUMBER: _ClassVar[int]
    SKIP_TRIAL_FIELD_NUMBER: _ClassVar[int]
    CANCEL_AFTER_TRIAL_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_COUPON_ID_FIELD_NUMBER: _ClassVar[int]
    plan: str
    skip_trial: bool
    cancel_after_trial: bool
    provider_coupon_id: str
    def __init__(self, plan: _Optional[str] = ..., skip_trial: _Optional[bool] = ..., cancel_after_trial: _Optional[bool] = ..., provider_coupon_id: _Optional[str] = ...) -> None: ...

class CheckoutProductBody(_message.Message):
    __slots__ = ("product", "quantity")
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    product: str
    quantity: int
    def __init__(self, product: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...

class CheckoutSetupBody(_message.Message):
    __slots__ = ("payment_method", "customer_portal")
    PAYMENT_METHOD_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_PORTAL_FIELD_NUMBER: _ClassVar[int]
    payment_method: bool
    customer_portal: bool
    def __init__(self, payment_method: _Optional[bool] = ..., customer_portal: _Optional[bool] = ...) -> None: ...

class Prospect(_message.Message):
    __slots__ = ("id", "name", "email", "phone", "activity", "status", "changed_at", "source", "verified", "created_at", "updated_at", "metadata")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[Prospect.Status]
        STATUS_UNSUBSCRIBED: _ClassVar[Prospect.Status]
        STATUS_SUBSCRIBED: _ClassVar[Prospect.Status]
    STATUS_UNSPECIFIED: Prospect.Status
    STATUS_UNSUBSCRIBED: Prospect.Status
    STATUS_SUBSCRIBED: Prospect.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CHANGED_AT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    email: str
    phone: str
    activity: str
    status: Prospect.Status
    changed_at: _timestamp_pb2.Timestamp
    source: str
    verified: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    metadata: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., activity: _Optional[str] = ..., status: _Optional[_Union[Prospect.Status, str]] = ..., changed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., source: _Optional[str] = ..., verified: _Optional[bool] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class RQLRequest(_message.Message):
    __slots__ = ("filters", "group_by", "offset", "limit", "search", "sort")
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    GROUP_BY_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.RepeatedCompositeFieldContainer[RQLFilter]
    group_by: _containers.RepeatedScalarFieldContainer[str]
    offset: int
    limit: int
    search: str
    sort: _containers.RepeatedCompositeFieldContainer[RQLSort]
    def __init__(self, filters: _Optional[_Iterable[_Union[RQLFilter, _Mapping]]] = ..., group_by: _Optional[_Iterable[str]] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ..., search: _Optional[str] = ..., sort: _Optional[_Iterable[_Union[RQLSort, _Mapping]]] = ...) -> None: ...

class RQLExportRequest(_message.Message):
    __slots__ = ("filters", "search", "sort")
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.RepeatedCompositeFieldContainer[RQLFilter]
    search: str
    sort: _containers.RepeatedCompositeFieldContainer[RQLSort]
    def __init__(self, filters: _Optional[_Iterable[_Union[RQLFilter, _Mapping]]] = ..., search: _Optional[str] = ..., sort: _Optional[_Iterable[_Union[RQLSort, _Mapping]]] = ...) -> None: ...

class RQLFilter(_message.Message):
    __slots__ = ("name", "operator", "bool_value", "string_value", "number_value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    operator: str
    bool_value: bool
    string_value: str
    number_value: float
    def __init__(self, name: _Optional[str] = ..., operator: _Optional[str] = ..., bool_value: _Optional[bool] = ..., string_value: _Optional[str] = ..., number_value: _Optional[float] = ...) -> None: ...

class RQLSort(_message.Message):
    __slots__ = ("name", "order")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    name: str
    order: str
    def __init__(self, name: _Optional[str] = ..., order: _Optional[str] = ...) -> None: ...

class RQLQueryPaginationResponse(_message.Message):
    __slots__ = ("offset", "limit", "total_count")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    offset: int
    limit: int
    total_count: int
    def __init__(self, offset: _Optional[int] = ..., limit: _Optional[int] = ..., total_count: _Optional[int] = ...) -> None: ...

class RQLQueryGroupResponse(_message.Message):
    __slots__ = ("name", "data")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    data: _containers.RepeatedCompositeFieldContainer[RQLQueryGroupData]
    def __init__(self, name: _Optional[str] = ..., data: _Optional[_Iterable[_Union[RQLQueryGroupData, _Mapping]]] = ...) -> None: ...

class RQLQueryGroupData(_message.Message):
    __slots__ = ("name", "count")
    NAME_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    name: str
    count: int
    def __init__(self, name: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class ExportOrganizationsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Session(_message.Message):
    __slots__ = ("id", "metadata", "is_current_session", "created_at", "updated_at")
    class Meta(_message.Message):
        __slots__ = ("operating_system", "browser", "ip_address", "location")
        OPERATING_SYSTEM_FIELD_NUMBER: _ClassVar[int]
        BROWSER_FIELD_NUMBER: _ClassVar[int]
        IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        LOCATION_FIELD_NUMBER: _ClassVar[int]
        operating_system: str
        browser: str
        ip_address: str
        location: str
        def __init__(self, operating_system: _Optional[str] = ..., browser: _Optional[str] = ..., ip_address: _Optional[str] = ..., location: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    IS_CURRENT_SESSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    metadata: Session.Meta
    is_current_session: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., metadata: _Optional[_Union[Session.Meta, _Mapping]] = ..., is_current_session: _Optional[bool] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AuditRecordActor(_message.Message):
    __slots__ = ("id", "type", "name", "metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    name: str
    metadata: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class AuditRecordResource(_message.Message):
    __slots__ = ("id", "type", "name", "metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    name: str
    metadata: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class AuditRecordTarget(_message.Message):
    __slots__ = ("id", "type", "name", "metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    name: str
    metadata: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class AuditRecord(_message.Message):
    __slots__ = ("id", "actor", "event", "resource", "target", "occurred_at", "org_id", "request_id", "metadata", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_AT_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    actor: AuditRecordActor
    event: str
    resource: AuditRecordResource
    target: AuditRecordTarget
    occurred_at: _timestamp_pb2.Timestamp
    org_id: str
    request_id: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., actor: _Optional[_Union[AuditRecordActor, _Mapping]] = ..., event: _Optional[str] = ..., resource: _Optional[_Union[AuditRecordResource, _Mapping]] = ..., target: _Optional[_Union[AuditRecordTarget, _Mapping]] = ..., occurred_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., org_id: _Optional[str] = ..., request_id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
