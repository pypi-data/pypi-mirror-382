import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
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

class ListProvidersRequest(_message.Message):
    __slots__ = ("type", "urn")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    type: str
    urn: str
    def __init__(self, type: _Optional[str] = ..., urn: _Optional[str] = ...) -> None: ...

class ListProvidersResponse(_message.Message):
    __slots__ = ("providers",)
    PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    providers: _containers.RepeatedCompositeFieldContainer[Provider]
    def __init__(self, providers: _Optional[_Iterable[_Union[Provider, _Mapping]]] = ...) -> None: ...

class GetProviderRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetProviderResponse(_message.Message):
    __slots__ = ("provider",)
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    provider: Provider
    def __init__(self, provider: _Optional[_Union[Provider, _Mapping]] = ...) -> None: ...

class GetProviderTypesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetProviderTypesResponse(_message.Message):
    __slots__ = ("provider_types",)
    PROVIDER_TYPES_FIELD_NUMBER: _ClassVar[int]
    provider_types: _containers.RepeatedCompositeFieldContainer[ProviderType]
    def __init__(self, provider_types: _Optional[_Iterable[_Union[ProviderType, _Mapping]]] = ...) -> None: ...

class CreateProviderRequest(_message.Message):
    __slots__ = ("config", "dry_run")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    config: ProviderConfig
    dry_run: bool
    def __init__(self, config: _Optional[_Union[ProviderConfig, _Mapping]] = ..., dry_run: _Optional[bool] = ...) -> None: ...

class CreateProviderResponse(_message.Message):
    __slots__ = ("provider",)
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    provider: Provider
    def __init__(self, provider: _Optional[_Union[Provider, _Mapping]] = ...) -> None: ...

class UpdateProviderRequest(_message.Message):
    __slots__ = ("id", "config", "dry_run")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    id: str
    config: ProviderConfig
    dry_run: bool
    def __init__(self, id: _Optional[str] = ..., config: _Optional[_Union[ProviderConfig, _Mapping]] = ..., dry_run: _Optional[bool] = ...) -> None: ...

class UpdateProviderResponse(_message.Message):
    __slots__ = ("provider",)
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    provider: Provider
    def __init__(self, provider: _Optional[_Union[Provider, _Mapping]] = ...) -> None: ...

class DeleteProviderRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteProviderResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ImportGrantsFromProviderRequest(_message.Message):
    __slots__ = ("provider_id", "resource_ids", "resource_types", "resource_urns")
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_IDS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_URNS_FIELD_NUMBER: _ClassVar[int]
    provider_id: str
    resource_ids: _containers.RepeatedScalarFieldContainer[str]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    resource_urns: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, provider_id: _Optional[str] = ..., resource_ids: _Optional[_Iterable[str]] = ..., resource_types: _Optional[_Iterable[str]] = ..., resource_urns: _Optional[_Iterable[str]] = ...) -> None: ...

class ImportGrantsFromProviderResponse(_message.Message):
    __slots__ = ("grants",)
    GRANTS_FIELD_NUMBER: _ClassVar[int]
    grants: _containers.RepeatedCompositeFieldContainer[Grant]
    def __init__(self, grants: _Optional[_Iterable[_Union[Grant, _Mapping]]] = ...) -> None: ...

class ListRolesRequest(_message.Message):
    __slots__ = ("id", "resource_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    resource_type: str
    def __init__(self, id: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class ListRolesResponse(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    def __init__(self, roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ...) -> None: ...

class ImportActivitiesRequest(_message.Message):
    __slots__ = ("provider_id", "account_ids", "resource_ids", "timestamp_gte", "timestamp_lte")
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_IDS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_IDS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_GTE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_LTE_FIELD_NUMBER: _ClassVar[int]
    provider_id: str
    account_ids: _containers.RepeatedScalarFieldContainer[str]
    resource_ids: _containers.RepeatedScalarFieldContainer[str]
    timestamp_gte: _timestamp_pb2.Timestamp
    timestamp_lte: _timestamp_pb2.Timestamp
    def __init__(self, provider_id: _Optional[str] = ..., account_ids: _Optional[_Iterable[str]] = ..., resource_ids: _Optional[_Iterable[str]] = ..., timestamp_gte: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., timestamp_lte: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ImportActivitiesResponse(_message.Message):
    __slots__ = ("activities",)
    ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    activities: _containers.RepeatedCompositeFieldContainer[ProviderActivity]
    def __init__(self, activities: _Optional[_Iterable[_Union[ProviderActivity, _Mapping]]] = ...) -> None: ...

class GetActivityRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetActivityResponse(_message.Message):
    __slots__ = ("activity",)
    ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    activity: ProviderActivity
    def __init__(self, activity: _Optional[_Union[ProviderActivity, _Mapping]] = ...) -> None: ...

class ListActivitiesRequest(_message.Message):
    __slots__ = ("provider_ids", "account_ids", "resource_ids", "types", "timestamp_gte", "timestamp_lte")
    PROVIDER_IDS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_IDS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_IDS_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_GTE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_LTE_FIELD_NUMBER: _ClassVar[int]
    provider_ids: _containers.RepeatedScalarFieldContainer[str]
    account_ids: _containers.RepeatedScalarFieldContainer[str]
    resource_ids: _containers.RepeatedScalarFieldContainer[str]
    types: _containers.RepeatedScalarFieldContainer[str]
    timestamp_gte: _timestamp_pb2.Timestamp
    timestamp_lte: _timestamp_pb2.Timestamp
    def __init__(self, provider_ids: _Optional[_Iterable[str]] = ..., account_ids: _Optional[_Iterable[str]] = ..., resource_ids: _Optional[_Iterable[str]] = ..., types: _Optional[_Iterable[str]] = ..., timestamp_gte: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., timestamp_lte: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListActivitiesResponse(_message.Message):
    __slots__ = ("activities",)
    ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    activities: _containers.RepeatedCompositeFieldContainer[ProviderActivity]
    def __init__(self, activities: _Optional[_Iterable[_Union[ProviderActivity, _Mapping]]] = ...) -> None: ...

class ListPoliciesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPoliciesResponse(_message.Message):
    __slots__ = ("policies",)
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    policies: _containers.RepeatedCompositeFieldContainer[Policy]
    def __init__(self, policies: _Optional[_Iterable[_Union[Policy, _Mapping]]] = ...) -> None: ...

class GetPolicyRequest(_message.Message):
    __slots__ = ("id", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    version: int
    def __init__(self, id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class GetPolicyPreferencesRequest(_message.Message):
    __slots__ = ("id", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    version: int
    def __init__(self, id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class GetPolicyPreferencesResponse(_message.Message):
    __slots__ = ("appeal",)
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    appeal: PolicyAppealConfig
    def __init__(self, appeal: _Optional[_Union[PolicyAppealConfig, _Mapping]] = ...) -> None: ...

class GetPolicyResponse(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: Policy
    def __init__(self, policy: _Optional[_Union[Policy, _Mapping]] = ...) -> None: ...

class CreatePolicyRequest(_message.Message):
    __slots__ = ("policy", "dry_run")
    POLICY_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    policy: Policy
    dry_run: bool
    def __init__(self, policy: _Optional[_Union[Policy, _Mapping]] = ..., dry_run: _Optional[bool] = ...) -> None: ...

class CreatePolicyResponse(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: Policy
    def __init__(self, policy: _Optional[_Union[Policy, _Mapping]] = ...) -> None: ...

class UpdatePolicyRequest(_message.Message):
    __slots__ = ("id", "policy", "dry_run")
    ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    id: str
    policy: Policy
    dry_run: bool
    def __init__(self, id: _Optional[str] = ..., policy: _Optional[_Union[Policy, _Mapping]] = ..., dry_run: _Optional[bool] = ...) -> None: ...

class UpdatePolicyResponse(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: Policy
    def __init__(self, policy: _Optional[_Union[Policy, _Mapping]] = ...) -> None: ...

class ListResourcesRequest(_message.Message):
    __slots__ = ("is_deleted", "provider_type", "provider_urn", "type", "urn", "name", "details")
    IS_DELETED_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_URN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    is_deleted: bool
    provider_type: str
    provider_urn: str
    type: str
    urn: str
    name: str
    details: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, is_deleted: _Optional[bool] = ..., provider_type: _Optional[str] = ..., provider_urn: _Optional[str] = ..., type: _Optional[str] = ..., urn: _Optional[str] = ..., name: _Optional[str] = ..., details: _Optional[_Iterable[str]] = ...) -> None: ...

class ListResourcesResponse(_message.Message):
    __slots__ = ("resources",)
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    resources: _containers.RepeatedCompositeFieldContainer[Resource]
    def __init__(self, resources: _Optional[_Iterable[_Union[Resource, _Mapping]]] = ...) -> None: ...

class GetResourceRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetResourceResponse(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: Resource
    def __init__(self, resource: _Optional[_Union[Resource, _Mapping]] = ...) -> None: ...

class UpdateResourceRequest(_message.Message):
    __slots__ = ("id", "resource")
    ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    resource: Resource
    def __init__(self, id: _Optional[str] = ..., resource: _Optional[_Union[Resource, _Mapping]] = ...) -> None: ...

class UpdateResourceResponse(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: Resource
    def __init__(self, resource: _Optional[_Union[Resource, _Mapping]] = ...) -> None: ...

class DeleteResourceRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteResourceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListUserAppealsRequest(_message.Message):
    __slots__ = ("statuses", "role", "provider_types", "provider_urns", "resource_types", "resource_urns", "order_by", "size", "offset", "q", "account_types")
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPES_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_URNS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_URNS_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPES_FIELD_NUMBER: _ClassVar[int]
    statuses: _containers.RepeatedScalarFieldContainer[str]
    role: str
    provider_types: _containers.RepeatedScalarFieldContainer[str]
    provider_urns: _containers.RepeatedScalarFieldContainer[str]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    resource_urns: _containers.RepeatedScalarFieldContainer[str]
    order_by: _containers.RepeatedScalarFieldContainer[str]
    size: int
    offset: int
    q: str
    account_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, statuses: _Optional[_Iterable[str]] = ..., role: _Optional[str] = ..., provider_types: _Optional[_Iterable[str]] = ..., provider_urns: _Optional[_Iterable[str]] = ..., resource_types: _Optional[_Iterable[str]] = ..., resource_urns: _Optional[_Iterable[str]] = ..., order_by: _Optional[_Iterable[str]] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ..., q: _Optional[str] = ..., account_types: _Optional[_Iterable[str]] = ...) -> None: ...

class ListUserAppealsResponse(_message.Message):
    __slots__ = ("appeals", "total")
    APPEALS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    appeals: _containers.RepeatedCompositeFieldContainer[Appeal]
    total: int
    def __init__(self, appeals: _Optional[_Iterable[_Union[Appeal, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class ListAppealsRequest(_message.Message):
    __slots__ = ("account_id", "statuses", "role", "provider_types", "provider_urns", "resource_types", "resource_urns", "order_by", "created_by", "size", "offset", "q", "account_types")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPES_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_URNS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_URNS_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPES_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    statuses: _containers.RepeatedScalarFieldContainer[str]
    role: str
    provider_types: _containers.RepeatedScalarFieldContainer[str]
    provider_urns: _containers.RepeatedScalarFieldContainer[str]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    resource_urns: _containers.RepeatedScalarFieldContainer[str]
    order_by: _containers.RepeatedScalarFieldContainer[str]
    created_by: str
    size: int
    offset: int
    q: str
    account_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, account_id: _Optional[str] = ..., statuses: _Optional[_Iterable[str]] = ..., role: _Optional[str] = ..., provider_types: _Optional[_Iterable[str]] = ..., provider_urns: _Optional[_Iterable[str]] = ..., resource_types: _Optional[_Iterable[str]] = ..., resource_urns: _Optional[_Iterable[str]] = ..., order_by: _Optional[_Iterable[str]] = ..., created_by: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ..., q: _Optional[str] = ..., account_types: _Optional[_Iterable[str]] = ...) -> None: ...

class ListAppealsResponse(_message.Message):
    __slots__ = ("appeals", "total")
    APPEALS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    appeals: _containers.RepeatedCompositeFieldContainer[Appeal]
    total: int
    def __init__(self, appeals: _Optional[_Iterable[_Union[Appeal, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class GetAppealRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetAppealResponse(_message.Message):
    __slots__ = ("appeal",)
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    appeal: Appeal
    def __init__(self, appeal: _Optional[_Union[Appeal, _Mapping]] = ...) -> None: ...

class CancelAppealRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class CancelAppealResponse(_message.Message):
    __slots__ = ("appeal",)
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    appeal: Appeal
    def __init__(self, appeal: _Optional[_Union[Appeal, _Mapping]] = ...) -> None: ...

class RevokeAppealRequest(_message.Message):
    __slots__ = ("id", "reason")
    class Reason(_message.Message):
        __slots__ = ("reason",)
        REASON_FIELD_NUMBER: _ClassVar[int]
        reason: str
        def __init__(self, reason: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    id: str
    reason: RevokeAppealRequest.Reason
    def __init__(self, id: _Optional[str] = ..., reason: _Optional[_Union[RevokeAppealRequest.Reason, _Mapping]] = ...) -> None: ...

class RevokeAppealResponse(_message.Message):
    __slots__ = ("appeal",)
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    appeal: Appeal
    def __init__(self, appeal: _Optional[_Union[Appeal, _Mapping]] = ...) -> None: ...

class RevokeAppealsRequest(_message.Message):
    __slots__ = ("account_ids", "provider_types", "provider_urns", "resource_types", "resource_urns", "reason")
    ACCOUNT_IDS_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPES_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_URNS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_URNS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    account_ids: _containers.RepeatedScalarFieldContainer[str]
    provider_types: _containers.RepeatedScalarFieldContainer[str]
    provider_urns: _containers.RepeatedScalarFieldContainer[str]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    resource_urns: _containers.RepeatedScalarFieldContainer[str]
    reason: str
    def __init__(self, account_ids: _Optional[_Iterable[str]] = ..., provider_types: _Optional[_Iterable[str]] = ..., provider_urns: _Optional[_Iterable[str]] = ..., resource_types: _Optional[_Iterable[str]] = ..., resource_urns: _Optional[_Iterable[str]] = ..., reason: _Optional[str] = ...) -> None: ...

class RevokeAppealsResponse(_message.Message):
    __slots__ = ("appeals",)
    APPEALS_FIELD_NUMBER: _ClassVar[int]
    appeals: _containers.RepeatedCompositeFieldContainer[Appeal]
    def __init__(self, appeals: _Optional[_Iterable[_Union[Appeal, _Mapping]]] = ...) -> None: ...

class CreateAppealRequest(_message.Message):
    __slots__ = ("account_id", "resources", "account_type", "description")
    class Resource(_message.Message):
        __slots__ = ("id", "role", "options", "details")
        ID_FIELD_NUMBER: _ClassVar[int]
        ROLE_FIELD_NUMBER: _ClassVar[int]
        OPTIONS_FIELD_NUMBER: _ClassVar[int]
        DETAILS_FIELD_NUMBER: _ClassVar[int]
        id: str
        role: str
        options: _struct_pb2.Struct
        details: _struct_pb2.Struct
        def __init__(self, id: _Optional[str] = ..., role: _Optional[str] = ..., options: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., details: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    resources: _containers.RepeatedCompositeFieldContainer[CreateAppealRequest.Resource]
    account_type: str
    description: str
    def __init__(self, account_id: _Optional[str] = ..., resources: _Optional[_Iterable[_Union[CreateAppealRequest.Resource, _Mapping]]] = ..., account_type: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class CreateAppealResponse(_message.Message):
    __slots__ = ("appeals",)
    APPEALS_FIELD_NUMBER: _ClassVar[int]
    appeals: _containers.RepeatedCompositeFieldContainer[Appeal]
    def __init__(self, appeals: _Optional[_Iterable[_Union[Appeal, _Mapping]]] = ...) -> None: ...

class ListUserApprovalsRequest(_message.Message):
    __slots__ = ("statuses", "order_by", "account_id", "size", "offset", "appeal_statuses", "q", "account_types", "resource_types")
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    APPEAL_STATUSES_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    statuses: _containers.RepeatedScalarFieldContainer[str]
    order_by: _containers.RepeatedScalarFieldContainer[str]
    account_id: str
    size: int
    offset: int
    appeal_statuses: _containers.RepeatedScalarFieldContainer[str]
    q: str
    account_types: _containers.RepeatedScalarFieldContainer[str]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, statuses: _Optional[_Iterable[str]] = ..., order_by: _Optional[_Iterable[str]] = ..., account_id: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ..., appeal_statuses: _Optional[_Iterable[str]] = ..., q: _Optional[str] = ..., account_types: _Optional[_Iterable[str]] = ..., resource_types: _Optional[_Iterable[str]] = ...) -> None: ...

class ListUserApprovalsResponse(_message.Message):
    __slots__ = ("approvals", "total")
    APPROVALS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    approvals: _containers.RepeatedCompositeFieldContainer[Approval]
    total: int
    def __init__(self, approvals: _Optional[_Iterable[_Union[Approval, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class ListApprovalsRequest(_message.Message):
    __slots__ = ("account_id", "statuses", "order_by", "created_by", "size", "offset", "appeal_statuses", "q", "account_types", "resource_types")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    APPEAL_STATUSES_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    statuses: _containers.RepeatedScalarFieldContainer[str]
    order_by: _containers.RepeatedScalarFieldContainer[str]
    created_by: str
    size: int
    offset: int
    appeal_statuses: _containers.RepeatedScalarFieldContainer[str]
    q: str
    account_types: _containers.RepeatedScalarFieldContainer[str]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, account_id: _Optional[str] = ..., statuses: _Optional[_Iterable[str]] = ..., order_by: _Optional[_Iterable[str]] = ..., created_by: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ..., appeal_statuses: _Optional[_Iterable[str]] = ..., q: _Optional[str] = ..., account_types: _Optional[_Iterable[str]] = ..., resource_types: _Optional[_Iterable[str]] = ...) -> None: ...

class ListApprovalsResponse(_message.Message):
    __slots__ = ("approvals", "total")
    APPROVALS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    approvals: _containers.RepeatedCompositeFieldContainer[Approval]
    total: int
    def __init__(self, approvals: _Optional[_Iterable[_Union[Approval, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class UpdateApprovalRequest(_message.Message):
    __slots__ = ("id", "approval_name", "action")
    class Action(_message.Message):
        __slots__ = ("action", "reason")
        ACTION_FIELD_NUMBER: _ClassVar[int]
        REASON_FIELD_NUMBER: _ClassVar[int]
        action: str
        reason: str
        def __init__(self, action: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    approval_name: str
    action: UpdateApprovalRequest.Action
    def __init__(self, id: _Optional[str] = ..., approval_name: _Optional[str] = ..., action: _Optional[_Union[UpdateApprovalRequest.Action, _Mapping]] = ...) -> None: ...

class UpdateApprovalResponse(_message.Message):
    __slots__ = ("appeal",)
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    appeal: Appeal
    def __init__(self, appeal: _Optional[_Union[Appeal, _Mapping]] = ...) -> None: ...

class AddApproverRequest(_message.Message):
    __slots__ = ("appeal_id", "approval_id", "email")
    APPEAL_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    appeal_id: str
    approval_id: str
    email: str
    def __init__(self, appeal_id: _Optional[str] = ..., approval_id: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...

class AddApproverResponse(_message.Message):
    __slots__ = ("appeal",)
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    appeal: Appeal
    def __init__(self, appeal: _Optional[_Union[Appeal, _Mapping]] = ...) -> None: ...

class DeleteApproverRequest(_message.Message):
    __slots__ = ("appeal_id", "approval_id", "email")
    APPEAL_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    appeal_id: str
    approval_id: str
    email: str
    def __init__(self, appeal_id: _Optional[str] = ..., approval_id: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...

class DeleteApproverResponse(_message.Message):
    __slots__ = ("appeal",)
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    appeal: Appeal
    def __init__(self, appeal: _Optional[_Union[Appeal, _Mapping]] = ...) -> None: ...

class ListGrantsRequest(_message.Message):
    __slots__ = ("statuses", "account_ids", "account_types", "resource_ids", "provider_types", "provider_urns", "resource_types", "resource_urns", "roles", "created_by", "order_by", "owner", "size", "offset", "q")
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_IDS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_IDS_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPES_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_URNS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_URNS_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    statuses: _containers.RepeatedScalarFieldContainer[str]
    account_ids: _containers.RepeatedScalarFieldContainer[str]
    account_types: _containers.RepeatedScalarFieldContainer[str]
    resource_ids: _containers.RepeatedScalarFieldContainer[str]
    provider_types: _containers.RepeatedScalarFieldContainer[str]
    provider_urns: _containers.RepeatedScalarFieldContainer[str]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    resource_urns: _containers.RepeatedScalarFieldContainer[str]
    roles: _containers.RepeatedScalarFieldContainer[str]
    created_by: str
    order_by: _containers.RepeatedScalarFieldContainer[str]
    owner: str
    size: int
    offset: int
    q: str
    def __init__(self, statuses: _Optional[_Iterable[str]] = ..., account_ids: _Optional[_Iterable[str]] = ..., account_types: _Optional[_Iterable[str]] = ..., resource_ids: _Optional[_Iterable[str]] = ..., provider_types: _Optional[_Iterable[str]] = ..., provider_urns: _Optional[_Iterable[str]] = ..., resource_types: _Optional[_Iterable[str]] = ..., resource_urns: _Optional[_Iterable[str]] = ..., roles: _Optional[_Iterable[str]] = ..., created_by: _Optional[str] = ..., order_by: _Optional[_Iterable[str]] = ..., owner: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ..., q: _Optional[str] = ...) -> None: ...

class ListGrantsResponse(_message.Message):
    __slots__ = ("grants", "total")
    GRANTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    grants: _containers.RepeatedCompositeFieldContainer[Grant]
    total: int
    def __init__(self, grants: _Optional[_Iterable[_Union[Grant, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class ListUserGrantsRequest(_message.Message):
    __slots__ = ("statuses", "account_ids", "account_types", "resource_ids", "provider_types", "provider_urns", "resource_types", "resource_urns", "roles", "order_by", "size", "offset", "q")
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_IDS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_IDS_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPES_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_URNS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_URNS_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    statuses: _containers.RepeatedScalarFieldContainer[str]
    account_ids: _containers.RepeatedScalarFieldContainer[str]
    account_types: _containers.RepeatedScalarFieldContainer[str]
    resource_ids: _containers.RepeatedScalarFieldContainer[str]
    provider_types: _containers.RepeatedScalarFieldContainer[str]
    provider_urns: _containers.RepeatedScalarFieldContainer[str]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    resource_urns: _containers.RepeatedScalarFieldContainer[str]
    roles: _containers.RepeatedScalarFieldContainer[str]
    order_by: _containers.RepeatedScalarFieldContainer[str]
    size: int
    offset: int
    q: str
    def __init__(self, statuses: _Optional[_Iterable[str]] = ..., account_ids: _Optional[_Iterable[str]] = ..., account_types: _Optional[_Iterable[str]] = ..., resource_ids: _Optional[_Iterable[str]] = ..., provider_types: _Optional[_Iterable[str]] = ..., provider_urns: _Optional[_Iterable[str]] = ..., resource_types: _Optional[_Iterable[str]] = ..., resource_urns: _Optional[_Iterable[str]] = ..., roles: _Optional[_Iterable[str]] = ..., order_by: _Optional[_Iterable[str]] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ..., q: _Optional[str] = ...) -> None: ...

class ListUserGrantsResponse(_message.Message):
    __slots__ = ("grants", "total")
    GRANTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    grants: _containers.RepeatedCompositeFieldContainer[Grant]
    total: int
    def __init__(self, grants: _Optional[_Iterable[_Union[Grant, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class GetGrantRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetGrantResponse(_message.Message):
    __slots__ = ("grant",)
    GRANT_FIELD_NUMBER: _ClassVar[int]
    grant: Grant
    def __init__(self, grant: _Optional[_Union[Grant, _Mapping]] = ...) -> None: ...

class UpdateGrantRequest(_message.Message):
    __slots__ = ("id", "owner")
    ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    id: str
    owner: str
    def __init__(self, id: _Optional[str] = ..., owner: _Optional[str] = ...) -> None: ...

class UpdateGrantResponse(_message.Message):
    __slots__ = ("grant",)
    GRANT_FIELD_NUMBER: _ClassVar[int]
    grant: Grant
    def __init__(self, grant: _Optional[_Union[Grant, _Mapping]] = ...) -> None: ...

class RevokeGrantRequest(_message.Message):
    __slots__ = ("id", "reason")
    ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    id: str
    reason: str
    def __init__(self, id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class RevokeGrantResponse(_message.Message):
    __slots__ = ("grant",)
    GRANT_FIELD_NUMBER: _ClassVar[int]
    grant: Grant
    def __init__(self, grant: _Optional[_Union[Grant, _Mapping]] = ...) -> None: ...

class RevokeGrantsRequest(_message.Message):
    __slots__ = ("account_ids", "provider_types", "provider_urns", "resource_types", "resource_urns", "reason")
    ACCOUNT_IDS_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPES_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_URNS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_URNS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    account_ids: _containers.RepeatedScalarFieldContainer[str]
    provider_types: _containers.RepeatedScalarFieldContainer[str]
    provider_urns: _containers.RepeatedScalarFieldContainer[str]
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    resource_urns: _containers.RepeatedScalarFieldContainer[str]
    reason: str
    def __init__(self, account_ids: _Optional[_Iterable[str]] = ..., provider_types: _Optional[_Iterable[str]] = ..., provider_urns: _Optional[_Iterable[str]] = ..., resource_types: _Optional[_Iterable[str]] = ..., resource_urns: _Optional[_Iterable[str]] = ..., reason: _Optional[str] = ...) -> None: ...

class RevokeGrantsResponse(_message.Message):
    __slots__ = ("grants",)
    GRANTS_FIELD_NUMBER: _ClassVar[int]
    grants: _containers.RepeatedCompositeFieldContainer[Grant]
    def __init__(self, grants: _Optional[_Iterable[_Union[Grant, _Mapping]]] = ...) -> None: ...

class Role(_message.Message):
    __slots__ = ("id", "name", "description", "permissions")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    permissions: _containers.RepeatedCompositeFieldContainer[_struct_pb2.Value]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., permissions: _Optional[_Iterable[_Union[_struct_pb2.Value, _Mapping]]] = ...) -> None: ...

class PolicyConfig(_message.Message):
    __slots__ = ("id", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    version: int
    def __init__(self, id: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class ProviderConfig(_message.Message):
    __slots__ = ("type", "urn", "labels", "credentials", "appeal", "resources", "allowed_account_types", "parameters")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class AppealConfig(_message.Message):
        __slots__ = ("allow_permanent_access", "allow_active_access_extension_in")
        ALLOW_PERMANENT_ACCESS_FIELD_NUMBER: _ClassVar[int]
        ALLOW_ACTIVE_ACCESS_EXTENSION_IN_FIELD_NUMBER: _ClassVar[int]
        allow_permanent_access: bool
        allow_active_access_extension_in: str
        def __init__(self, allow_permanent_access: _Optional[bool] = ..., allow_active_access_extension_in: _Optional[str] = ...) -> None: ...
    class ResourceConfig(_message.Message):
        __slots__ = ("type", "policy", "roles", "filter")
        TYPE_FIELD_NUMBER: _ClassVar[int]
        POLICY_FIELD_NUMBER: _ClassVar[int]
        ROLES_FIELD_NUMBER: _ClassVar[int]
        FILTER_FIELD_NUMBER: _ClassVar[int]
        type: str
        policy: PolicyConfig
        roles: _containers.RepeatedCompositeFieldContainer[Role]
        filter: str
        def __init__(self, type: _Optional[str] = ..., policy: _Optional[_Union[PolicyConfig, _Mapping]] = ..., roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ..., filter: _Optional[str] = ...) -> None: ...
    class ProviderParameter(_message.Message):
        __slots__ = ("key", "label", "required", "description")
        KEY_FIELD_NUMBER: _ClassVar[int]
        LABEL_FIELD_NUMBER: _ClassVar[int]
        REQUIRED_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        key: str
        label: str
        required: bool
        description: str
        def __init__(self, key: _Optional[str] = ..., label: _Optional[str] = ..., required: _Optional[bool] = ..., description: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_ACCOUNT_TYPES_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    type: str
    urn: str
    labels: _containers.ScalarMap[str, str]
    credentials: _struct_pb2.Value
    appeal: ProviderConfig.AppealConfig
    resources: _containers.RepeatedCompositeFieldContainer[ProviderConfig.ResourceConfig]
    allowed_account_types: _containers.RepeatedScalarFieldContainer[str]
    parameters: _containers.RepeatedCompositeFieldContainer[ProviderConfig.ProviderParameter]
    def __init__(self, type: _Optional[str] = ..., urn: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., credentials: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., appeal: _Optional[_Union[ProviderConfig.AppealConfig, _Mapping]] = ..., resources: _Optional[_Iterable[_Union[ProviderConfig.ResourceConfig, _Mapping]]] = ..., allowed_account_types: _Optional[_Iterable[str]] = ..., parameters: _Optional[_Iterable[_Union[ProviderConfig.ProviderParameter, _Mapping]]] = ...) -> None: ...

class Provider(_message.Message):
    __slots__ = ("id", "type", "urn", "config", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    urn: str
    config: ProviderConfig
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., urn: _Optional[str] = ..., config: _Optional[_Union[ProviderConfig, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ProviderType(_message.Message):
    __slots__ = ("name", "resource_types")
    NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    name: str
    resource_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., resource_types: _Optional[_Iterable[str]] = ...) -> None: ...

class Condition(_message.Message):
    __slots__ = ("field", "match")
    class MatchCondition(_message.Message):
        __slots__ = ("eq",)
        EQ_FIELD_NUMBER: _ClassVar[int]
        eq: _struct_pb2.Value
        def __init__(self, eq: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
    FIELD_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    field: str
    match: Condition.MatchCondition
    def __init__(self, field: _Optional[str] = ..., match: _Optional[_Union[Condition.MatchCondition, _Mapping]] = ...) -> None: ...

class PolicyAppealConfig(_message.Message):
    __slots__ = ("duration_options", "allow_on_behalf", "allow_permanent_access", "allow_active_access_extension_in", "questions", "allow_creator_details_failure")
    class DurationOptions(_message.Message):
        __slots__ = ("name", "value")
        NAME_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        name: str
        value: str
        def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class Question(_message.Message):
        __slots__ = ("key", "question", "required", "description")
        KEY_FIELD_NUMBER: _ClassVar[int]
        QUESTION_FIELD_NUMBER: _ClassVar[int]
        REQUIRED_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        key: str
        question: str
        required: bool
        description: str
        def __init__(self, key: _Optional[str] = ..., question: _Optional[str] = ..., required: _Optional[bool] = ..., description: _Optional[str] = ...) -> None: ...
    DURATION_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_ON_BEHALF_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PERMANENT_ACCESS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_ACTIVE_ACCESS_EXTENSION_IN_FIELD_NUMBER: _ClassVar[int]
    QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_CREATOR_DETAILS_FAILURE_FIELD_NUMBER: _ClassVar[int]
    duration_options: _containers.RepeatedCompositeFieldContainer[PolicyAppealConfig.DurationOptions]
    allow_on_behalf: bool
    allow_permanent_access: bool
    allow_active_access_extension_in: str
    questions: _containers.RepeatedCompositeFieldContainer[PolicyAppealConfig.Question]
    allow_creator_details_failure: bool
    def __init__(self, duration_options: _Optional[_Iterable[_Union[PolicyAppealConfig.DurationOptions, _Mapping]]] = ..., allow_on_behalf: _Optional[bool] = ..., allow_permanent_access: _Optional[bool] = ..., allow_active_access_extension_in: _Optional[str] = ..., questions: _Optional[_Iterable[_Union[PolicyAppealConfig.Question, _Mapping]]] = ..., allow_creator_details_failure: _Optional[bool] = ...) -> None: ...

class Policy(_message.Message):
    __slots__ = ("id", "version", "description", "steps", "labels", "created_at", "updated_at", "requirements", "iam", "appeal", "title", "created_by")
    class ApprovalStep(_message.Message):
        __slots__ = ("name", "description", "allow_failed", "when", "strategy", "approve_if", "approvers", "rejection_reason")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        ALLOW_FAILED_FIELD_NUMBER: _ClassVar[int]
        WHEN_FIELD_NUMBER: _ClassVar[int]
        STRATEGY_FIELD_NUMBER: _ClassVar[int]
        APPROVE_IF_FIELD_NUMBER: _ClassVar[int]
        APPROVERS_FIELD_NUMBER: _ClassVar[int]
        REJECTION_REASON_FIELD_NUMBER: _ClassVar[int]
        name: str
        description: str
        allow_failed: bool
        when: str
        strategy: str
        approve_if: str
        approvers: _containers.RepeatedScalarFieldContainer[str]
        rejection_reason: str
        def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., allow_failed: _Optional[bool] = ..., when: _Optional[str] = ..., strategy: _Optional[str] = ..., approve_if: _Optional[str] = ..., approvers: _Optional[_Iterable[str]] = ..., rejection_reason: _Optional[str] = ...) -> None: ...
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class Requirement(_message.Message):
        __slots__ = ("on", "appeals")
        class RequirementTrigger(_message.Message):
            __slots__ = ("provider_type", "provider_urn", "resource_type", "resource_urn", "role", "conditions", "expression")
            PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
            PROVIDER_URN_FIELD_NUMBER: _ClassVar[int]
            RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
            RESOURCE_URN_FIELD_NUMBER: _ClassVar[int]
            ROLE_FIELD_NUMBER: _ClassVar[int]
            CONDITIONS_FIELD_NUMBER: _ClassVar[int]
            EXPRESSION_FIELD_NUMBER: _ClassVar[int]
            provider_type: str
            provider_urn: str
            resource_type: str
            resource_urn: str
            role: str
            conditions: _containers.RepeatedCompositeFieldContainer[Condition]
            expression: str
            def __init__(self, provider_type: _Optional[str] = ..., provider_urn: _Optional[str] = ..., resource_type: _Optional[str] = ..., resource_urn: _Optional[str] = ..., role: _Optional[str] = ..., conditions: _Optional[_Iterable[_Union[Condition, _Mapping]]] = ..., expression: _Optional[str] = ...) -> None: ...
        class AdditionalAppeal(_message.Message):
            __slots__ = ("resource", "role", "options", "policy")
            class ResourceIdentifier(_message.Message):
                __slots__ = ("provider_type", "provider_urn", "type", "urn", "id")
                PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
                PROVIDER_URN_FIELD_NUMBER: _ClassVar[int]
                TYPE_FIELD_NUMBER: _ClassVar[int]
                URN_FIELD_NUMBER: _ClassVar[int]
                ID_FIELD_NUMBER: _ClassVar[int]
                provider_type: str
                provider_urn: str
                type: str
                urn: str
                id: str
                def __init__(self, provider_type: _Optional[str] = ..., provider_urn: _Optional[str] = ..., type: _Optional[str] = ..., urn: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...
            RESOURCE_FIELD_NUMBER: _ClassVar[int]
            ROLE_FIELD_NUMBER: _ClassVar[int]
            OPTIONS_FIELD_NUMBER: _ClassVar[int]
            POLICY_FIELD_NUMBER: _ClassVar[int]
            resource: Policy.Requirement.AdditionalAppeal.ResourceIdentifier
            role: str
            options: AppealOptions
            policy: PolicyConfig
            def __init__(self, resource: _Optional[_Union[Policy.Requirement.AdditionalAppeal.ResourceIdentifier, _Mapping]] = ..., role: _Optional[str] = ..., options: _Optional[_Union[AppealOptions, _Mapping]] = ..., policy: _Optional[_Union[PolicyConfig, _Mapping]] = ...) -> None: ...
        ON_FIELD_NUMBER: _ClassVar[int]
        APPEALS_FIELD_NUMBER: _ClassVar[int]
        on: Policy.Requirement.RequirementTrigger
        appeals: _containers.RepeatedCompositeFieldContainer[Policy.Requirement.AdditionalAppeal]
        def __init__(self, on: _Optional[_Union[Policy.Requirement.RequirementTrigger, _Mapping]] = ..., appeals: _Optional[_Iterable[_Union[Policy.Requirement.AdditionalAppeal, _Mapping]]] = ...) -> None: ...
    class IAM(_message.Message):
        __slots__ = ("provider", "config", "schema")
        class SchemaEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        PROVIDER_FIELD_NUMBER: _ClassVar[int]
        CONFIG_FIELD_NUMBER: _ClassVar[int]
        SCHEMA_FIELD_NUMBER: _ClassVar[int]
        provider: str
        config: _struct_pb2.Value
        schema: _containers.ScalarMap[str, str]
        def __init__(self, provider: _Optional[str] = ..., config: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., schema: _Optional[_Mapping[str, str]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    IAM_FIELD_NUMBER: _ClassVar[int]
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    id: str
    version: int
    description: str
    steps: _containers.RepeatedCompositeFieldContainer[Policy.ApprovalStep]
    labels: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    requirements: _containers.RepeatedCompositeFieldContainer[Policy.Requirement]
    iam: Policy.IAM
    appeal: PolicyAppealConfig
    title: str
    created_by: str
    def __init__(self, id: _Optional[str] = ..., version: _Optional[int] = ..., description: _Optional[str] = ..., steps: _Optional[_Iterable[_Union[Policy.ApprovalStep, _Mapping]]] = ..., labels: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., requirements: _Optional[_Iterable[_Union[Policy.Requirement, _Mapping]]] = ..., iam: _Optional[_Union[Policy.IAM, _Mapping]] = ..., appeal: _Optional[_Union[PolicyAppealConfig, _Mapping]] = ..., title: _Optional[str] = ..., created_by: _Optional[str] = ...) -> None: ...

class AppealOptions(_message.Message):
    __slots__ = ("expiration_date", "duration")
    EXPIRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    expiration_date: _timestamp_pb2.Timestamp
    duration: str
    def __init__(self, expiration_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[str] = ...) -> None: ...

class Appeal(_message.Message):
    __slots__ = ("id", "resource_id", "policy_id", "policy_version", "status", "account_id", "role", "options", "labels", "resource", "approvals", "created_at", "updated_at", "details", "account_type", "created_by", "creator", "permissions", "grant", "description")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    APPROVALS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    GRANT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    resource_id: str
    policy_id: str
    policy_version: int
    status: str
    account_id: str
    role: str
    options: AppealOptions
    labels: _containers.ScalarMap[str, str]
    resource: Resource
    approvals: _containers.RepeatedCompositeFieldContainer[Approval]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    details: _struct_pb2.Struct
    account_type: str
    created_by: str
    creator: _struct_pb2.Value
    permissions: _containers.RepeatedScalarFieldContainer[str]
    grant: Grant
    description: str
    def __init__(self, id: _Optional[str] = ..., resource_id: _Optional[str] = ..., policy_id: _Optional[str] = ..., policy_version: _Optional[int] = ..., status: _Optional[str] = ..., account_id: _Optional[str] = ..., role: _Optional[str] = ..., options: _Optional[_Union[AppealOptions, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., resource: _Optional[_Union[Resource, _Mapping]] = ..., approvals: _Optional[_Iterable[_Union[Approval, _Mapping]]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., details: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., account_type: _Optional[str] = ..., created_by: _Optional[str] = ..., creator: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., permissions: _Optional[_Iterable[str]] = ..., grant: _Optional[_Union[Grant, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class Approval(_message.Message):
    __slots__ = ("id", "name", "appeal_id", "status", "actor", "policy_id", "policy_version", "approvers", "appeal", "created_at", "updated_at", "reason")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    APPEAL_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_FIELD_NUMBER: _ClassVar[int]
    APPROVERS_FIELD_NUMBER: _ClassVar[int]
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    appeal_id: str
    status: str
    actor: str
    policy_id: str
    policy_version: int
    approvers: _containers.RepeatedScalarFieldContainer[str]
    appeal: Appeal
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    reason: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., appeal_id: _Optional[str] = ..., status: _Optional[str] = ..., actor: _Optional[str] = ..., policy_id: _Optional[str] = ..., policy_version: _Optional[int] = ..., approvers: _Optional[_Iterable[str]] = ..., appeal: _Optional[_Union[Appeal, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., reason: _Optional[str] = ...) -> None: ...

class Resource(_message.Message):
    __slots__ = ("id", "provider_type", "provider_urn", "type", "urn", "name", "details", "labels", "created_at", "updated_at", "is_deleted", "parent_id", "children")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_URN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_DELETED_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    id: str
    provider_type: str
    provider_urn: str
    type: str
    urn: str
    name: str
    details: _struct_pb2.Struct
    labels: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    is_deleted: bool
    parent_id: str
    children: _containers.RepeatedCompositeFieldContainer[Resource]
    def __init__(self, id: _Optional[str] = ..., provider_type: _Optional[str] = ..., provider_urn: _Optional[str] = ..., type: _Optional[str] = ..., urn: _Optional[str] = ..., name: _Optional[str] = ..., details: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., is_deleted: _Optional[bool] = ..., parent_id: _Optional[str] = ..., children: _Optional[_Iterable[_Union[Resource, _Mapping]]] = ...) -> None: ...

class Grant(_message.Message):
    __slots__ = ("id", "status", "account_id", "account_type", "resource_id", "role", "permissions", "expiration_date", "appeal_id", "revoked_by", "revoked_at", "revoke_reason", "created_by", "created_at", "updated_at", "resource", "appeal", "is_permanent", "source", "status_in_provider", "owner")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    APPEAL_ID_FIELD_NUMBER: _ClassVar[int]
    REVOKED_BY_FIELD_NUMBER: _ClassVar[int]
    REVOKED_AT_FIELD_NUMBER: _ClassVar[int]
    REVOKE_REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    APPEAL_FIELD_NUMBER: _ClassVar[int]
    IS_PERMANENT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STATUS_IN_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: str
    account_id: str
    account_type: str
    resource_id: str
    role: str
    permissions: _containers.RepeatedScalarFieldContainer[str]
    expiration_date: _timestamp_pb2.Timestamp
    appeal_id: str
    revoked_by: str
    revoked_at: _timestamp_pb2.Timestamp
    revoke_reason: str
    created_by: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    resource: Resource
    appeal: Appeal
    is_permanent: bool
    source: str
    status_in_provider: str
    owner: str
    def __init__(self, id: _Optional[str] = ..., status: _Optional[str] = ..., account_id: _Optional[str] = ..., account_type: _Optional[str] = ..., resource_id: _Optional[str] = ..., role: _Optional[str] = ..., permissions: _Optional[_Iterable[str]] = ..., expiration_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., appeal_id: _Optional[str] = ..., revoked_by: _Optional[str] = ..., revoked_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., revoke_reason: _Optional[str] = ..., created_by: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., resource: _Optional[_Union[Resource, _Mapping]] = ..., appeal: _Optional[_Union[Appeal, _Mapping]] = ..., is_permanent: _Optional[bool] = ..., source: _Optional[str] = ..., status_in_provider: _Optional[str] = ..., owner: _Optional[str] = ...) -> None: ...

class ProviderActivity(_message.Message):
    __slots__ = ("id", "provider_id", "resource_id", "account_id", "account_type", "timestamp", "authorizations", "type", "metadata", "created_at", "provider", "resource", "provider_activity_id", "related_permissions")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATIONS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    RELATED_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    provider_id: str
    resource_id: str
    account_id: str
    account_type: str
    timestamp: _timestamp_pb2.Timestamp
    authorizations: _containers.RepeatedScalarFieldContainer[str]
    type: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    provider: Provider
    resource: Resource
    provider_activity_id: str
    related_permissions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., provider_id: _Optional[str] = ..., resource_id: _Optional[str] = ..., account_id: _Optional[str] = ..., account_type: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., authorizations: _Optional[_Iterable[str]] = ..., type: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., provider: _Optional[_Union[Provider, _Mapping]] = ..., resource: _Optional[_Union[Resource, _Mapping]] = ..., provider_activity_id: _Optional[str] = ..., related_permissions: _Optional[_Iterable[str]] = ...) -> None: ...

class Namespace(_message.Message):
    __slots__ = ("id", "name", "state", "metadata", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    state: str
    metadata: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., state: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateNamespaceRequest(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: Namespace
    def __init__(self, namespace: _Optional[_Union[Namespace, _Mapping]] = ...) -> None: ...

class CreateNamespaceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

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

class ListNamespacesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNamespacesResponse(_message.Message):
    __slots__ = ("namespaces",)
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    namespaces: _containers.RepeatedCompositeFieldContainer[Namespace]
    def __init__(self, namespaces: _Optional[_Iterable[_Union[Namespace, _Mapping]]] = ...) -> None: ...

class UpdateNamespaceRequest(_message.Message):
    __slots__ = ("id", "namespace")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    id: str
    namespace: Namespace
    def __init__(self, id: _Optional[str] = ..., namespace: _Optional[_Union[Namespace, _Mapping]] = ...) -> None: ...

class UpdateNamespaceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
