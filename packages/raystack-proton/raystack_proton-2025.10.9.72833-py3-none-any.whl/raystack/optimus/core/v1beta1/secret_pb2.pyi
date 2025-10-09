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

class RegisterSecretRequest(_message.Message):
    __slots__ = ("project_name", "secret_name", "value", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    SECRET_NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    secret_name: str
    value: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., secret_name: _Optional[str] = ..., value: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class RegisterSecretResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateSecretRequest(_message.Message):
    __slots__ = ("project_name", "secret_name", "value", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    SECRET_NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    secret_name: str
    value: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., secret_name: _Optional[str] = ..., value: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class UpdateSecretResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSecretsRequest(_message.Message):
    __slots__ = ("project_name",)
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    def __init__(self, project_name: _Optional[str] = ...) -> None: ...

class ListSecretsResponse(_message.Message):
    __slots__ = ("secrets",)
    class Secret(_message.Message):
        __slots__ = ("name", "digest", "namespace", "updated_at")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DIGEST_FIELD_NUMBER: _ClassVar[int]
        NAMESPACE_FIELD_NUMBER: _ClassVar[int]
        UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
        name: str
        digest: str
        namespace: str
        updated_at: _timestamp_pb2.Timestamp
        def __init__(self, name: _Optional[str] = ..., digest: _Optional[str] = ..., namespace: _Optional[str] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    secrets: _containers.RepeatedCompositeFieldContainer[ListSecretsResponse.Secret]
    def __init__(self, secrets: _Optional[_Iterable[_Union[ListSecretsResponse.Secret, _Mapping]]] = ...) -> None: ...

class DeleteSecretRequest(_message.Message):
    __slots__ = ("project_name", "secret_name", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    SECRET_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    secret_name: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., secret_name: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class DeleteSecretResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
