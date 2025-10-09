import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Provider(_message.Message):
    __slots__ = ("id", "host", "urn", "name", "type", "credentials", "labels", "created_at", "updated_at")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    host: str
    urn: str
    name: str
    type: str
    credentials: _struct_pb2.Struct
    labels: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., host: _Optional[str] = ..., urn: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., credentials: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListProvidersRequest(_message.Message):
    __slots__ = ("urn", "type")
    URN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    urn: str
    type: str
    def __init__(self, urn: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class ListProvidersResponse(_message.Message):
    __slots__ = ("providers",)
    PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    providers: _containers.RepeatedCompositeFieldContainer[Provider]
    def __init__(self, providers: _Optional[_Iterable[_Union[Provider, _Mapping]]] = ...) -> None: ...

class CreateProviderRequest(_message.Message):
    __slots__ = ("host", "urn", "name", "type", "credentials", "labels")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    HOST_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    host: str
    urn: str
    name: str
    type: str
    credentials: _struct_pb2.Struct
    labels: _containers.ScalarMap[str, str]
    def __init__(self, host: _Optional[str] = ..., urn: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., credentials: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CreateProviderResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetProviderRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetProviderResponse(_message.Message):
    __slots__ = ("provider",)
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    provider: Provider
    def __init__(self, provider: _Optional[_Union[Provider, _Mapping]] = ...) -> None: ...

class UpdateProviderRequest(_message.Message):
    __slots__ = ("id", "host", "name", "type", "credentials", "labels")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    id: int
    host: str
    name: str
    type: str
    credentials: _struct_pb2.Struct
    labels: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[int] = ..., host: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., credentials: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UpdateProviderResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteProviderRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteProviderResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Namespace(_message.Message):
    __slots__ = ("id", "urn", "name", "provider", "credentials", "labels", "created_at", "updated_at")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    urn: str
    name: str
    provider: int
    credentials: _struct_pb2.Struct
    labels: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., urn: _Optional[str] = ..., name: _Optional[str] = ..., provider: _Optional[int] = ..., credentials: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListNamespacesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNamespacesResponse(_message.Message):
    __slots__ = ("namespaces",)
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    namespaces: _containers.RepeatedCompositeFieldContainer[Namespace]
    def __init__(self, namespaces: _Optional[_Iterable[_Union[Namespace, _Mapping]]] = ...) -> None: ...

class CreateNamespaceRequest(_message.Message):
    __slots__ = ("name", "urn", "provider", "credentials", "labels", "created_at", "updated_at")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    urn: str
    provider: int
    credentials: _struct_pb2.Struct
    labels: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., urn: _Optional[str] = ..., provider: _Optional[int] = ..., credentials: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateNamespaceResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetNamespaceRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetNamespaceResponse(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: Namespace
    def __init__(self, namespace: _Optional[_Union[Namespace, _Mapping]] = ...) -> None: ...

class UpdateNamespaceRequest(_message.Message):
    __slots__ = ("id", "name", "provider", "credentials", "labels")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    provider: int
    credentials: _struct_pb2.Struct
    labels: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., provider: _Optional[int] = ..., credentials: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UpdateNamespaceResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteNamespaceRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteNamespaceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReceiverMetadata(_message.Message):
    __slots__ = ("id", "configuration")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    id: int
    configuration: _struct_pb2.Struct
    def __init__(self, id: _Optional[int] = ..., configuration: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class Subscription(_message.Message):
    __slots__ = ("id", "urn", "namespace", "receivers", "match", "created_at", "updated_at")
    class MatchEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    RECEIVERS_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    urn: str
    namespace: int
    receivers: _containers.RepeatedCompositeFieldContainer[ReceiverMetadata]
    match: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., urn: _Optional[str] = ..., namespace: _Optional[int] = ..., receivers: _Optional[_Iterable[_Union[ReceiverMetadata, _Mapping]]] = ..., match: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListSubscriptionsRequest(_message.Message):
    __slots__ = ("namespace_id", "match", "notification_match", "silence_id")
    class MatchEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class NotificationMatchEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_MATCH_FIELD_NUMBER: _ClassVar[int]
    SILENCE_ID_FIELD_NUMBER: _ClassVar[int]
    namespace_id: int
    match: _containers.ScalarMap[str, str]
    notification_match: _containers.ScalarMap[str, str]
    silence_id: str
    def __init__(self, namespace_id: _Optional[int] = ..., match: _Optional[_Mapping[str, str]] = ..., notification_match: _Optional[_Mapping[str, str]] = ..., silence_id: _Optional[str] = ...) -> None: ...

class ListSubscriptionsResponse(_message.Message):
    __slots__ = ("subscriptions",)
    SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    subscriptions: _containers.RepeatedCompositeFieldContainer[Subscription]
    def __init__(self, subscriptions: _Optional[_Iterable[_Union[Subscription, _Mapping]]] = ...) -> None: ...

class CreateSubscriptionRequest(_message.Message):
    __slots__ = ("urn", "namespace", "receivers", "match")
    class MatchEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URN_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    RECEIVERS_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    urn: str
    namespace: int
    receivers: _containers.RepeatedCompositeFieldContainer[ReceiverMetadata]
    match: _containers.ScalarMap[str, str]
    def __init__(self, urn: _Optional[str] = ..., namespace: _Optional[int] = ..., receivers: _Optional[_Iterable[_Union[ReceiverMetadata, _Mapping]]] = ..., match: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CreateSubscriptionResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetSubscriptionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetSubscriptionResponse(_message.Message):
    __slots__ = ("subscription",)
    SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    subscription: Subscription
    def __init__(self, subscription: _Optional[_Union[Subscription, _Mapping]] = ...) -> None: ...

class UpdateSubscriptionRequest(_message.Message):
    __slots__ = ("id", "urn", "namespace", "receivers", "match")
    class MatchEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    RECEIVERS_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    id: int
    urn: str
    namespace: int
    receivers: _containers.RepeatedCompositeFieldContainer[ReceiverMetadata]
    match: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[int] = ..., urn: _Optional[str] = ..., namespace: _Optional[int] = ..., receivers: _Optional[_Iterable[_Union[ReceiverMetadata, _Mapping]]] = ..., match: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UpdateSubscriptionResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteSubscriptionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteSubscriptionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Receiver(_message.Message):
    __slots__ = ("id", "name", "type", "labels", "configurations", "data", "created_at", "updated_at")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    type: str
    labels: _containers.ScalarMap[str, str]
    configurations: _struct_pb2.Struct
    data: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., configurations: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListReceiversRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListReceiversResponse(_message.Message):
    __slots__ = ("receivers",)
    RECEIVERS_FIELD_NUMBER: _ClassVar[int]
    receivers: _containers.RepeatedCompositeFieldContainer[Receiver]
    def __init__(self, receivers: _Optional[_Iterable[_Union[Receiver, _Mapping]]] = ...) -> None: ...

class CreateReceiverRequest(_message.Message):
    __slots__ = ("name", "type", "labels", "configurations")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    labels: _containers.ScalarMap[str, str]
    configurations: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., configurations: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateReceiverResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetReceiverRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetReceiverResponse(_message.Message):
    __slots__ = ("receiver",)
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    receiver: Receiver
    def __init__(self, receiver: _Optional[_Union[Receiver, _Mapping]] = ...) -> None: ...

class UpdateReceiverRequest(_message.Message):
    __slots__ = ("id", "name", "labels", "configurations")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    labels: _containers.ScalarMap[str, str]
    configurations: _struct_pb2.Struct
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., configurations: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdateReceiverResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteReceiverRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteReceiverResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NotifyReceiverRequest(_message.Message):
    __slots__ = ("id", "payload")
    ID_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    id: int
    payload: _struct_pb2.Struct
    def __init__(self, id: _Optional[int] = ..., payload: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class NotifyReceiverResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Alert(_message.Message):
    __slots__ = ("id", "provider_id", "resource_name", "metric_name", "metric_value", "severity", "rule", "triggered_at", "namespace_id", "silence_status")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    METRIC_NAME_FIELD_NUMBER: _ClassVar[int]
    METRIC_VALUE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    RULE_FIELD_NUMBER: _ClassVar[int]
    TRIGGERED_AT_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SILENCE_STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    provider_id: int
    resource_name: str
    metric_name: str
    metric_value: str
    severity: str
    rule: str
    triggered_at: _timestamp_pb2.Timestamp
    namespace_id: int
    silence_status: str
    def __init__(self, id: _Optional[int] = ..., provider_id: _Optional[int] = ..., resource_name: _Optional[str] = ..., metric_name: _Optional[str] = ..., metric_value: _Optional[str] = ..., severity: _Optional[str] = ..., rule: _Optional[str] = ..., triggered_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., namespace_id: _Optional[int] = ..., silence_status: _Optional[str] = ...) -> None: ...

class ListAlertsRequest(_message.Message):
    __slots__ = ("provider_type", "provider_id", "resource_name", "start_time", "end_time", "namespace_id", "silence_id")
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    SILENCE_ID_FIELD_NUMBER: _ClassVar[int]
    provider_type: str
    provider_id: int
    resource_name: str
    start_time: int
    end_time: int
    namespace_id: int
    silence_id: str
    def __init__(self, provider_type: _Optional[str] = ..., provider_id: _Optional[int] = ..., resource_name: _Optional[str] = ..., start_time: _Optional[int] = ..., end_time: _Optional[int] = ..., namespace_id: _Optional[int] = ..., silence_id: _Optional[str] = ...) -> None: ...

class ListAlertsResponse(_message.Message):
    __slots__ = ("alerts",)
    ALERTS_FIELD_NUMBER: _ClassVar[int]
    alerts: _containers.RepeatedCompositeFieldContainer[Alert]
    def __init__(self, alerts: _Optional[_Iterable[_Union[Alert, _Mapping]]] = ...) -> None: ...

class CreateAlertsRequest(_message.Message):
    __slots__ = ("provider_type", "provider_id", "body")
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    provider_type: str
    provider_id: int
    body: _struct_pb2.Struct
    def __init__(self, provider_type: _Optional[str] = ..., provider_id: _Optional[int] = ..., body: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateAlertsResponse(_message.Message):
    __slots__ = ("alerts",)
    ALERTS_FIELD_NUMBER: _ClassVar[int]
    alerts: _containers.RepeatedCompositeFieldContainer[Alert]
    def __init__(self, alerts: _Optional[_Iterable[_Union[Alert, _Mapping]]] = ...) -> None: ...

class CreateAlertsWithNamespaceRequest(_message.Message):
    __slots__ = ("provider_type", "provider_id", "body", "namespace_id")
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    provider_type: str
    provider_id: int
    body: _struct_pb2.Struct
    namespace_id: int
    def __init__(self, provider_type: _Optional[str] = ..., provider_id: _Optional[int] = ..., body: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., namespace_id: _Optional[int] = ...) -> None: ...

class CreateAlertsWithNamespaceResponse(_message.Message):
    __slots__ = ("alerts",)
    ALERTS_FIELD_NUMBER: _ClassVar[int]
    alerts: _containers.RepeatedCompositeFieldContainer[Alert]
    def __init__(self, alerts: _Optional[_Iterable[_Union[Alert, _Mapping]]] = ...) -> None: ...

class Annotations(_message.Message):
    __slots__ = ("metric_name", "metric_value", "resource", "template")
    METRIC_NAME_FIELD_NUMBER: _ClassVar[int]
    METRIC_VALUE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    metric_name: str
    metric_value: str
    resource: str
    template: str
    def __init__(self, metric_name: _Optional[str] = ..., metric_value: _Optional[str] = ..., resource: _Optional[str] = ..., template: _Optional[str] = ...) -> None: ...

class Labels(_message.Message):
    __slots__ = ("severity",)
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    severity: str
    def __init__(self, severity: _Optional[str] = ...) -> None: ...

class Rule(_message.Message):
    __slots__ = ("id", "name", "enabled", "group_name", "namespace", "template", "variables", "created_at", "updated_at", "provider_namespace")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    enabled: bool
    group_name: str
    namespace: str
    template: str
    variables: _containers.RepeatedCompositeFieldContainer[Variables]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    provider_namespace: int
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., enabled: _Optional[bool] = ..., group_name: _Optional[str] = ..., namespace: _Optional[str] = ..., template: _Optional[str] = ..., variables: _Optional[_Iterable[_Union[Variables, _Mapping]]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., provider_namespace: _Optional[int] = ...) -> None: ...

class Variables(_message.Message):
    __slots__ = ("name", "value", "type", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    type: str
    description: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., type: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class ListRulesRequest(_message.Message):
    __slots__ = ("name", "namespace", "group_name", "template", "provider_namespace")
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    group_name: str
    template: str
    provider_namespace: int
    def __init__(self, name: _Optional[str] = ..., namespace: _Optional[str] = ..., group_name: _Optional[str] = ..., template: _Optional[str] = ..., provider_namespace: _Optional[int] = ...) -> None: ...

class ListRulesResponse(_message.Message):
    __slots__ = ("rules",)
    RULES_FIELD_NUMBER: _ClassVar[int]
    rules: _containers.RepeatedCompositeFieldContainer[Rule]
    def __init__(self, rules: _Optional[_Iterable[_Union[Rule, _Mapping]]] = ...) -> None: ...

class UpdateRuleRequest(_message.Message):
    __slots__ = ("enabled", "group_name", "namespace", "template", "variables", "provider_namespace")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    group_name: str
    namespace: str
    template: str
    variables: _containers.RepeatedCompositeFieldContainer[Variables]
    provider_namespace: int
    def __init__(self, enabled: _Optional[bool] = ..., group_name: _Optional[str] = ..., namespace: _Optional[str] = ..., template: _Optional[str] = ..., variables: _Optional[_Iterable[_Union[Variables, _Mapping]]] = ..., provider_namespace: _Optional[int] = ...) -> None: ...

class UpdateRuleResponse(_message.Message):
    __slots__ = ("rule",)
    RULE_FIELD_NUMBER: _ClassVar[int]
    rule: Rule
    def __init__(self, rule: _Optional[_Union[Rule, _Mapping]] = ...) -> None: ...

class TemplateVariables(_message.Message):
    __slots__ = ("name", "type", "default", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    default: str
    description: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., default: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class Template(_message.Message):
    __slots__ = ("id", "name", "body", "tags", "created_at", "updated_at", "variables")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    body: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    variables: _containers.RepeatedCompositeFieldContainer[TemplateVariables]
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., body: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., variables: _Optional[_Iterable[_Union[TemplateVariables, _Mapping]]] = ...) -> None: ...

class ListTemplatesRequest(_message.Message):
    __slots__ = ("tag",)
    TAG_FIELD_NUMBER: _ClassVar[int]
    tag: str
    def __init__(self, tag: _Optional[str] = ...) -> None: ...

class ListTemplatesResponse(_message.Message):
    __slots__ = ("templates",)
    TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    templates: _containers.RepeatedCompositeFieldContainer[Template]
    def __init__(self, templates: _Optional[_Iterable[_Union[Template, _Mapping]]] = ...) -> None: ...

class UpsertTemplateRequest(_message.Message):
    __slots__ = ("id", "name", "body", "tags", "variables")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    body: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    variables: _containers.RepeatedCompositeFieldContainer[TemplateVariables]
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., body: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., variables: _Optional[_Iterable[_Union[TemplateVariables, _Mapping]]] = ...) -> None: ...

class UpsertTemplateResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetTemplateRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetTemplateResponse(_message.Message):
    __slots__ = ("template",)
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    template: Template
    def __init__(self, template: _Optional[_Union[Template, _Mapping]] = ...) -> None: ...

class DeleteTemplateRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class DeleteTemplateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RenderTemplateRequest(_message.Message):
    __slots__ = ("name", "variables")
    class VariablesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    name: str
    variables: _containers.ScalarMap[str, str]
    def __init__(self, name: _Optional[str] = ..., variables: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RenderTemplateResponse(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: str
    def __init__(self, body: _Optional[str] = ...) -> None: ...

class Silence(_message.Message):
    __slots__ = ("id", "namespace_id", "type", "target_id", "target_expression", "created_at", "updated_at", "deleted_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    namespace_id: int
    type: str
    target_id: int
    target_expression: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    deleted_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., namespace_id: _Optional[int] = ..., type: _Optional[str] = ..., target_id: _Optional[int] = ..., target_expression: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., deleted_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateSilenceRequest(_message.Message):
    __slots__ = ("namespace_id", "type", "target_id", "target_expression")
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    namespace_id: int
    type: str
    target_id: int
    target_expression: _struct_pb2.Struct
    def __init__(self, namespace_id: _Optional[int] = ..., type: _Optional[str] = ..., target_id: _Optional[int] = ..., target_expression: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateSilenceResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListSilencesRequest(_message.Message):
    __slots__ = ("subscription_id", "namespace_id", "match", "subscription_match")
    class MatchEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class SubscriptionMatchEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_ID_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_MATCH_FIELD_NUMBER: _ClassVar[int]
    subscription_id: int
    namespace_id: int
    match: _containers.ScalarMap[str, str]
    subscription_match: _containers.ScalarMap[str, str]
    def __init__(self, subscription_id: _Optional[int] = ..., namespace_id: _Optional[int] = ..., match: _Optional[_Mapping[str, str]] = ..., subscription_match: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ListSilencesResponse(_message.Message):
    __slots__ = ("silences",)
    SILENCES_FIELD_NUMBER: _ClassVar[int]
    silences: _containers.RepeatedCompositeFieldContainer[Silence]
    def __init__(self, silences: _Optional[_Iterable[_Union[Silence, _Mapping]]] = ...) -> None: ...

class GetSilenceRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetSilenceResponse(_message.Message):
    __slots__ = ("silence",)
    SILENCE_FIELD_NUMBER: _ClassVar[int]
    silence: Silence
    def __init__(self, silence: _Optional[_Union[Silence, _Mapping]] = ...) -> None: ...

class ExpireSilenceRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ExpireSilenceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
