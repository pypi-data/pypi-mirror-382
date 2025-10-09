import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.api import httpbody_pb2 as _httpbody_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from raystack.frontier.v1beta1 import models_pb2 as _models_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListAllUsersRequest(_message.Message):
    __slots__ = ("page_size", "page_num", "keyword", "org_id", "group_id", "state")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_NUM_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_num: int
    keyword: str
    org_id: str
    group_id: str
    state: str
    def __init__(self, page_size: _Optional[int] = ..., page_num: _Optional[int] = ..., keyword: _Optional[str] = ..., org_id: _Optional[str] = ..., group_id: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class ListAllUsersResponse(_message.Message):
    __slots__ = ("count", "users")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    count: int
    users: _containers.RepeatedCompositeFieldContainer[_models_pb2.User]
    def __init__(self, count: _Optional[int] = ..., users: _Optional[_Iterable[_Union[_models_pb2.User, _Mapping]]] = ...) -> None: ...

class ListAllServiceUsersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListAllServiceUsersResponse(_message.Message):
    __slots__ = ("service_users",)
    SERVICE_USERS_FIELD_NUMBER: _ClassVar[int]
    service_users: _containers.RepeatedCompositeFieldContainer[_models_pb2.ServiceUser]
    def __init__(self, service_users: _Optional[_Iterable[_Union[_models_pb2.ServiceUser, _Mapping]]] = ...) -> None: ...

class ListGroupsRequest(_message.Message):
    __slots__ = ("org_id", "state")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    state: str
    def __init__(self, org_id: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class ListGroupsResponse(_message.Message):
    __slots__ = ("groups",)
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_models_pb2.Group]
    def __init__(self, groups: _Optional[_Iterable[_Union[_models_pb2.Group, _Mapping]]] = ...) -> None: ...

class ListAllOrganizationsRequest(_message.Message):
    __slots__ = ("user_id", "state", "page_size", "page_num")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_NUM_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    state: str
    page_size: int
    page_num: int
    def __init__(self, user_id: _Optional[str] = ..., state: _Optional[str] = ..., page_size: _Optional[int] = ..., page_num: _Optional[int] = ...) -> None: ...

class ListAllOrganizationsResponse(_message.Message):
    __slots__ = ("organizations", "count")
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Organization]
    count: int
    def __init__(self, organizations: _Optional[_Iterable[_Union[_models_pb2.Organization, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class ListProjectsRequest(_message.Message):
    __slots__ = ("org_id", "state")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    state: str
    def __init__(self, org_id: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class ListProjectsResponse(_message.Message):
    __slots__ = ("projects",)
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[_models_pb2.Project]
    def __init__(self, projects: _Optional[_Iterable[_Union[_models_pb2.Project, _Mapping]]] = ...) -> None: ...

class ListRelationsRequest(_message.Message):
    __slots__ = ("subject", "object")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    subject: str
    object: str
    def __init__(self, subject: _Optional[str] = ..., object: _Optional[str] = ...) -> None: ...

class ListRelationsResponse(_message.Message):
    __slots__ = ("relations",)
    RELATIONS_FIELD_NUMBER: _ClassVar[int]
    relations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Relation]
    def __init__(self, relations: _Optional[_Iterable[_Union[_models_pb2.Relation, _Mapping]]] = ...) -> None: ...

class ListResourcesRequest(_message.Message):
    __slots__ = ("user_id", "project_id", "organization_id", "namespace")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    project_id: str
    organization_id: str
    namespace: str
    def __init__(self, user_id: _Optional[str] = ..., project_id: _Optional[str] = ..., organization_id: _Optional[str] = ..., namespace: _Optional[str] = ...) -> None: ...

class ListResourcesResponse(_message.Message):
    __slots__ = ("resources",)
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    resources: _containers.RepeatedCompositeFieldContainer[_models_pb2.Resource]
    def __init__(self, resources: _Optional[_Iterable[_Union[_models_pb2.Resource, _Mapping]]] = ...) -> None: ...

class CreateRoleRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: _models_pb2.RoleRequestBody
    def __init__(self, body: _Optional[_Union[_models_pb2.RoleRequestBody, _Mapping]] = ...) -> None: ...

class CreateRoleResponse(_message.Message):
    __slots__ = ("role",)
    ROLE_FIELD_NUMBER: _ClassVar[int]
    role: _models_pb2.Role
    def __init__(self, role: _Optional[_Union[_models_pb2.Role, _Mapping]] = ...) -> None: ...

class UpdateRoleRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: _models_pb2.RoleRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[_models_pb2.RoleRequestBody, _Mapping]] = ...) -> None: ...

class UpdateRoleResponse(_message.Message):
    __slots__ = ("role",)
    ROLE_FIELD_NUMBER: _ClassVar[int]
    role: _models_pb2.Role
    def __init__(self, role: _Optional[_Union[_models_pb2.Role, _Mapping]] = ...) -> None: ...

class DeleteRoleRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteRoleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PermissionRequestBody(_message.Message):
    __slots__ = ("name", "namespace", "metadata", "title", "key")
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    metadata: _struct_pb2.Struct
    title: str
    key: str
    def __init__(self, name: _Optional[str] = ..., namespace: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., title: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class CreatePermissionRequest(_message.Message):
    __slots__ = ("bodies",)
    BODIES_FIELD_NUMBER: _ClassVar[int]
    bodies: _containers.RepeatedCompositeFieldContainer[PermissionRequestBody]
    def __init__(self, bodies: _Optional[_Iterable[_Union[PermissionRequestBody, _Mapping]]] = ...) -> None: ...

class CreatePermissionResponse(_message.Message):
    __slots__ = ("permissions",)
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[_models_pb2.Permission]
    def __init__(self, permissions: _Optional[_Iterable[_Union[_models_pb2.Permission, _Mapping]]] = ...) -> None: ...

class UpdatePermissionRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: PermissionRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[PermissionRequestBody, _Mapping]] = ...) -> None: ...

class UpdatePermissionResponse(_message.Message):
    __slots__ = ("permission",)
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    permission: _models_pb2.Permission
    def __init__(self, permission: _Optional[_Union[_models_pb2.Permission, _Mapping]] = ...) -> None: ...

class DeletePermissionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeletePermissionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPreferencesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class CreatePreferencesRequest(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.PreferenceRequestBody]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.PreferenceRequestBody, _Mapping]]] = ...) -> None: ...

class CreatePreferencesResponse(_message.Message):
    __slots__ = ("preference",)
    PREFERENCE_FIELD_NUMBER: _ClassVar[int]
    preference: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preference: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class CheckFederatedResourcePermissionRequest(_message.Message):
    __slots__ = ("subject", "resource", "permission")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    subject: str
    resource: str
    permission: str
    def __init__(self, subject: _Optional[str] = ..., resource: _Optional[str] = ..., permission: _Optional[str] = ...) -> None: ...

class CheckFederatedResourcePermissionResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: _Optional[bool] = ...) -> None: ...

class AddPlatformUserRequest(_message.Message):
    __slots__ = ("user_id", "serviceuser_id", "relation")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SERVICEUSER_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    serviceuser_id: str
    relation: str
    def __init__(self, user_id: _Optional[str] = ..., serviceuser_id: _Optional[str] = ..., relation: _Optional[str] = ...) -> None: ...

class AddPlatformUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPlatformUsersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPlatformUsersResponse(_message.Message):
    __slots__ = ("users", "serviceusers")
    USERS_FIELD_NUMBER: _ClassVar[int]
    SERVICEUSERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_models_pb2.User]
    serviceusers: _containers.RepeatedCompositeFieldContainer[_models_pb2.ServiceUser]
    def __init__(self, users: _Optional[_Iterable[_Union[_models_pb2.User, _Mapping]]] = ..., serviceusers: _Optional[_Iterable[_Union[_models_pb2.ServiceUser, _Mapping]]] = ...) -> None: ...

class RemovePlatformUserRequest(_message.Message):
    __slots__ = ("user_id", "serviceuser_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SERVICEUSER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    serviceuser_id: str
    def __init__(self, user_id: _Optional[str] = ..., serviceuser_id: _Optional[str] = ...) -> None: ...

class RemovePlatformUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DelegatedCheckoutRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "subscription_body", "product_body")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_BODY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_BODY_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    subscription_body: _models_pb2.CheckoutSubscriptionBody
    product_body: _models_pb2.CheckoutProductBody
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., subscription_body: _Optional[_Union[_models_pb2.CheckoutSubscriptionBody, _Mapping]] = ..., product_body: _Optional[_Union[_models_pb2.CheckoutProductBody, _Mapping]] = ...) -> None: ...

class DelegatedCheckoutResponse(_message.Message):
    __slots__ = ("subscription", "product")
    SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    subscription: _models_pb2.Subscription
    product: _models_pb2.Product
    def __init__(self, subscription: _Optional[_Union[_models_pb2.Subscription, _Mapping]] = ..., product: _Optional[_Union[_models_pb2.Product, _Mapping]] = ...) -> None: ...

class ListAllInvoicesRequest(_message.Message):
    __slots__ = ("org_id", "page_size", "page_num")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_NUM_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    page_size: int
    page_num: int
    def __init__(self, org_id: _Optional[str] = ..., page_size: _Optional[int] = ..., page_num: _Optional[int] = ...) -> None: ...

class ListAllInvoicesResponse(_message.Message):
    __slots__ = ("invoices", "count")
    INVOICES_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    invoices: _containers.RepeatedCompositeFieldContainer[_models_pb2.Invoice]
    count: int
    def __init__(self, invoices: _Optional[_Iterable[_Union[_models_pb2.Invoice, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class GenerateInvoicesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GenerateInvoicesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListAllBillingAccountsRequest(_message.Message):
    __slots__ = ("org_id",)
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    def __init__(self, org_id: _Optional[str] = ...) -> None: ...

class ListAllBillingAccountsResponse(_message.Message):
    __slots__ = ("billing_accounts",)
    BILLING_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    billing_accounts: _containers.RepeatedCompositeFieldContainer[_models_pb2.BillingAccount]
    def __init__(self, billing_accounts: _Optional[_Iterable[_Union[_models_pb2.BillingAccount, _Mapping]]] = ...) -> None: ...

class RevertBillingUsageRequest(_message.Message):
    __slots__ = ("org_id", "project_id", "billing_id", "usage_id", "amount")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    USAGE_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    project_id: str
    billing_id: str
    usage_id: str
    amount: int
    def __init__(self, org_id: _Optional[str] = ..., project_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., usage_id: _Optional[str] = ..., amount: _Optional[int] = ...) -> None: ...

class RevertBillingUsageResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WebhookRequestBody(_message.Message):
    __slots__ = ("url", "description", "subscribed_events", "headers", "state", "metadata")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_EVENTS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    url: str
    description: str
    subscribed_events: _containers.RepeatedScalarFieldContainer[str]
    headers: _containers.ScalarMap[str, str]
    state: str
    metadata: _struct_pb2.Struct
    def __init__(self, url: _Optional[str] = ..., description: _Optional[str] = ..., subscribed_events: _Optional[_Iterable[str]] = ..., headers: _Optional[_Mapping[str, str]] = ..., state: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateWebhookRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: WebhookRequestBody
    def __init__(self, body: _Optional[_Union[WebhookRequestBody, _Mapping]] = ...) -> None: ...

class CreateWebhookResponse(_message.Message):
    __slots__ = ("webhook",)
    WEBHOOK_FIELD_NUMBER: _ClassVar[int]
    webhook: _models_pb2.Webhook
    def __init__(self, webhook: _Optional[_Union[_models_pb2.Webhook, _Mapping]] = ...) -> None: ...

class UpdateWebhookRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: WebhookRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[WebhookRequestBody, _Mapping]] = ...) -> None: ...

class UpdateWebhookResponse(_message.Message):
    __slots__ = ("webhook",)
    WEBHOOK_FIELD_NUMBER: _ClassVar[int]
    webhook: _models_pb2.Webhook
    def __init__(self, webhook: _Optional[_Union[_models_pb2.Webhook, _Mapping]] = ...) -> None: ...

class DeleteWebhookRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteWebhookResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListWebhooksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListWebhooksResponse(_message.Message):
    __slots__ = ("webhooks",)
    WEBHOOKS_FIELD_NUMBER: _ClassVar[int]
    webhooks: _containers.RepeatedCompositeFieldContainer[_models_pb2.Webhook]
    def __init__(self, webhooks: _Optional[_Iterable[_Union[_models_pb2.Webhook, _Mapping]]] = ...) -> None: ...

class UpdateBillingAccountLimitsRequest(_message.Message):
    __slots__ = ("org_id", "id", "credit_min")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    CREDIT_MIN_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    id: str
    credit_min: int
    def __init__(self, org_id: _Optional[str] = ..., id: _Optional[str] = ..., credit_min: _Optional[int] = ...) -> None: ...

class UpdateBillingAccountLimitsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetBillingAccountDetailsRequest(_message.Message):
    __slots__ = ("org_id", "id")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    id: str
    def __init__(self, org_id: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class GetBillingAccountDetailsResponse(_message.Message):
    __slots__ = ("credit_min", "due_in_days")
    CREDIT_MIN_FIELD_NUMBER: _ClassVar[int]
    DUE_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    credit_min: int
    due_in_days: int
    def __init__(self, credit_min: _Optional[int] = ..., due_in_days: _Optional[int] = ...) -> None: ...

class UpdateBillingAccountDetailsRequest(_message.Message):
    __slots__ = ("org_id", "id", "credit_min", "due_in_days")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    CREDIT_MIN_FIELD_NUMBER: _ClassVar[int]
    DUE_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    id: str
    credit_min: int
    due_in_days: int
    def __init__(self, org_id: _Optional[str] = ..., id: _Optional[str] = ..., credit_min: _Optional[int] = ..., due_in_days: _Optional[int] = ...) -> None: ...

class UpdateBillingAccountDetailsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetOrganizationKycRequest(_message.Message):
    __slots__ = ("org_id", "status", "link")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    status: bool
    link: str
    def __init__(self, org_id: _Optional[str] = ..., status: _Optional[bool] = ..., link: _Optional[str] = ...) -> None: ...

class SearchOrganizationsRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: _models_pb2.RQLRequest
    def __init__(self, query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SetOrganizationKycResponse(_message.Message):
    __slots__ = ("organization_kyc",)
    ORGANIZATION_KYC_FIELD_NUMBER: _ClassVar[int]
    organization_kyc: _models_pb2.OrganizationKyc
    def __init__(self, organization_kyc: _Optional[_Union[_models_pb2.OrganizationKyc, _Mapping]] = ...) -> None: ...

class ListOrganizationsKycRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListOrganizationsKycResponse(_message.Message):
    __slots__ = ("organizations_kyc",)
    ORGANIZATIONS_KYC_FIELD_NUMBER: _ClassVar[int]
    organizations_kyc: _containers.RepeatedCompositeFieldContainer[_models_pb2.OrganizationKyc]
    def __init__(self, organizations_kyc: _Optional[_Iterable[_Union[_models_pb2.OrganizationKyc, _Mapping]]] = ...) -> None: ...

class SearchOrganizationsResponse(_message.Message):
    __slots__ = ("organizations", "pagination", "group")
    class OrganizationResult(_message.Message):
        __slots__ = ("id", "name", "title", "created_at", "updated_at", "state", "avatar", "created_by", "plan_name", "payment_mode", "subscription_cycle_end_at", "country", "subscription_state", "plan_interval", "plan_id")
        ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        AVATAR_FIELD_NUMBER: _ClassVar[int]
        CREATED_BY_FIELD_NUMBER: _ClassVar[int]
        PLAN_NAME_FIELD_NUMBER: _ClassVar[int]
        PAYMENT_MODE_FIELD_NUMBER: _ClassVar[int]
        SUBSCRIPTION_CYCLE_END_AT_FIELD_NUMBER: _ClassVar[int]
        COUNTRY_FIELD_NUMBER: _ClassVar[int]
        SUBSCRIPTION_STATE_FIELD_NUMBER: _ClassVar[int]
        PLAN_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        PLAN_ID_FIELD_NUMBER: _ClassVar[int]
        id: str
        name: str
        title: str
        created_at: _timestamp_pb2.Timestamp
        updated_at: _timestamp_pb2.Timestamp
        state: str
        avatar: str
        created_by: str
        plan_name: str
        payment_mode: str
        subscription_cycle_end_at: _timestamp_pb2.Timestamp
        country: str
        subscription_state: str
        plan_interval: str
        plan_id: str
        def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[str] = ..., avatar: _Optional[str] = ..., created_by: _Optional[str] = ..., plan_name: _Optional[str] = ..., payment_mode: _Optional[str] = ..., subscription_cycle_end_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., country: _Optional[str] = ..., subscription_state: _Optional[str] = ..., plan_interval: _Optional[str] = ..., plan_id: _Optional[str] = ...) -> None: ...
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[SearchOrganizationsResponse.OrganizationResult]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, organizations: _Optional[_Iterable[_Union[SearchOrganizationsResponse.OrganizationResult, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class ListProspectsRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: _models_pb2.RQLRequest
    def __init__(self, query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class ListProspectsResponse(_message.Message):
    __slots__ = ("prospects", "pagination", "group")
    PROSPECTS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    prospects: _containers.RepeatedCompositeFieldContainer[_models_pb2.Prospect]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, prospects: _Optional[_Iterable[_Union[_models_pb2.Prospect, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class GetProspectRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetProspectResponse(_message.Message):
    __slots__ = ("prospect",)
    PROSPECT_FIELD_NUMBER: _ClassVar[int]
    prospect: _models_pb2.Prospect
    def __init__(self, prospect: _Optional[_Union[_models_pb2.Prospect, _Mapping]] = ...) -> None: ...

class UpdateProspectRequest(_message.Message):
    __slots__ = ("id", "name", "email", "phone", "activity", "status", "source", "verified", "metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    email: str
    phone: str
    activity: str
    status: _models_pb2.Prospect.Status
    source: str
    verified: bool
    metadata: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., activity: _Optional[str] = ..., status: _Optional[_Union[_models_pb2.Prospect.Status, str]] = ..., source: _Optional[str] = ..., verified: _Optional[bool] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdateProspectResponse(_message.Message):
    __slots__ = ("prospect",)
    PROSPECT_FIELD_NUMBER: _ClassVar[int]
    prospect: _models_pb2.Prospect
    def __init__(self, prospect: _Optional[_Union[_models_pb2.Prospect, _Mapping]] = ...) -> None: ...

class DeleteProspectRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteProspectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateProspectRequest(_message.Message):
    __slots__ = ("name", "email", "phone", "activity", "status", "source", "verified", "metadata")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    email: str
    phone: str
    activity: str
    status: _models_pb2.Prospect.Status
    source: str
    verified: bool
    metadata: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., activity: _Optional[str] = ..., status: _Optional[_Union[_models_pb2.Prospect.Status, str]] = ..., source: _Optional[str] = ..., verified: _Optional[bool] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateProspectResponse(_message.Message):
    __slots__ = ("prospect",)
    PROSPECT_FIELD_NUMBER: _ClassVar[int]
    prospect: _models_pb2.Prospect
    def __init__(self, prospect: _Optional[_Union[_models_pb2.Prospect, _Mapping]] = ...) -> None: ...

class SearchOrganizationUsersRequest(_message.Message):
    __slots__ = ("id", "query")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    query: _models_pb2.RQLRequest
    def __init__(self, id: _Optional[str] = ..., query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchOrganizationUsersResponse(_message.Message):
    __slots__ = ("org_users", "pagination", "group")
    class OrganizationUser(_message.Message):
        __slots__ = ("id", "name", "title", "email", "org_joined_at", "state", "avatar", "role_names", "role_titles", "role_ids", "organization_id")
        ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        EMAIL_FIELD_NUMBER: _ClassVar[int]
        ORG_JOINED_AT_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        AVATAR_FIELD_NUMBER: _ClassVar[int]
        ROLE_NAMES_FIELD_NUMBER: _ClassVar[int]
        ROLE_TITLES_FIELD_NUMBER: _ClassVar[int]
        ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        id: str
        name: str
        title: str
        email: str
        org_joined_at: _timestamp_pb2.Timestamp
        state: str
        avatar: str
        role_names: _containers.RepeatedScalarFieldContainer[str]
        role_titles: _containers.RepeatedScalarFieldContainer[str]
        role_ids: _containers.RepeatedScalarFieldContainer[str]
        organization_id: str
        def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., email: _Optional[str] = ..., org_joined_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[str] = ..., avatar: _Optional[str] = ..., role_names: _Optional[_Iterable[str]] = ..., role_titles: _Optional[_Iterable[str]] = ..., role_ids: _Optional[_Iterable[str]] = ..., organization_id: _Optional[str] = ...) -> None: ...
    ORG_USERS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    org_users: _containers.RepeatedCompositeFieldContainer[SearchOrganizationUsersResponse.OrganizationUser]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, org_users: _Optional[_Iterable[_Union[SearchOrganizationUsersResponse.OrganizationUser, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class ExportOrganizationUsersRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class SearchOrganizationProjectsRequest(_message.Message):
    __slots__ = ("id", "query")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    query: _models_pb2.RQLRequest
    def __init__(self, id: _Optional[str] = ..., query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchOrganizationProjectsResponse(_message.Message):
    __slots__ = ("org_projects", "pagination", "group")
    class OrganizationProject(_message.Message):
        __slots__ = ("id", "name", "title", "state", "member_count", "user_ids", "created_at", "organization_id")
        ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
        USER_IDS_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        id: str
        name: str
        title: str
        state: str
        member_count: int
        user_ids: _containers.RepeatedScalarFieldContainer[str]
        created_at: _timestamp_pb2.Timestamp
        organization_id: str
        def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., state: _Optional[str] = ..., member_count: _Optional[int] = ..., user_ids: _Optional[_Iterable[str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., organization_id: _Optional[str] = ...) -> None: ...
    ORG_PROJECTS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    org_projects: _containers.RepeatedCompositeFieldContainer[SearchOrganizationProjectsResponse.OrganizationProject]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, org_projects: _Optional[_Iterable[_Union[SearchOrganizationProjectsResponse.OrganizationProject, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class ExportOrganizationProjectsRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class SearchProjectUsersRequest(_message.Message):
    __slots__ = ("id", "query")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    query: _models_pb2.RQLRequest
    def __init__(self, id: _Optional[str] = ..., query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchProjectUsersResponse(_message.Message):
    __slots__ = ("project_users", "pagination", "group")
    class ProjectUser(_message.Message):
        __slots__ = ("id", "name", "title", "email", "avatar", "role_names", "role_titles", "role_ids", "project_id")
        ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        EMAIL_FIELD_NUMBER: _ClassVar[int]
        AVATAR_FIELD_NUMBER: _ClassVar[int]
        ROLE_NAMES_FIELD_NUMBER: _ClassVar[int]
        ROLE_TITLES_FIELD_NUMBER: _ClassVar[int]
        ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
        PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
        id: str
        name: str
        title: str
        email: str
        avatar: str
        role_names: _containers.RepeatedScalarFieldContainer[str]
        role_titles: _containers.RepeatedScalarFieldContainer[str]
        role_ids: _containers.RepeatedScalarFieldContainer[str]
        project_id: str
        def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., title: _Optional[str] = ..., email: _Optional[str] = ..., avatar: _Optional[str] = ..., role_names: _Optional[_Iterable[str]] = ..., role_titles: _Optional[_Iterable[str]] = ..., role_ids: _Optional[_Iterable[str]] = ..., project_id: _Optional[str] = ...) -> None: ...
    PROJECT_USERS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    project_users: _containers.RepeatedCompositeFieldContainer[SearchProjectUsersResponse.ProjectUser]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, project_users: _Optional[_Iterable[_Union[SearchProjectUsersResponse.ProjectUser, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class SearchOrganizationInvoicesRequest(_message.Message):
    __slots__ = ("id", "query")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    query: _models_pb2.RQLRequest
    def __init__(self, id: _Optional[str] = ..., query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchOrganizationInvoicesResponse(_message.Message):
    __slots__ = ("organization_invoices", "pagination", "group")
    class OrganizationInvoice(_message.Message):
        __slots__ = ("id", "amount", "currency", "state", "invoice_link", "created_at", "org_id")
        ID_FIELD_NUMBER: _ClassVar[int]
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        CURRENCY_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        INVOICE_LINK_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        ORG_ID_FIELD_NUMBER: _ClassVar[int]
        id: str
        amount: int
        currency: str
        state: str
        invoice_link: str
        created_at: _timestamp_pb2.Timestamp
        org_id: str
        def __init__(self, id: _Optional[str] = ..., amount: _Optional[int] = ..., currency: _Optional[str] = ..., state: _Optional[str] = ..., invoice_link: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., org_id: _Optional[str] = ...) -> None: ...
    ORGANIZATION_INVOICES_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    organization_invoices: _containers.RepeatedCompositeFieldContainer[SearchOrganizationInvoicesResponse.OrganizationInvoice]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, organization_invoices: _Optional[_Iterable[_Union[SearchOrganizationInvoicesResponse.OrganizationInvoice, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class SearchOrganizationTokensRequest(_message.Message):
    __slots__ = ("id", "query")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    query: _models_pb2.RQLRequest
    def __init__(self, id: _Optional[str] = ..., query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchOrganizationTokensResponse(_message.Message):
    __slots__ = ("organization_tokens", "pagination", "group")
    class OrganizationToken(_message.Message):
        __slots__ = ("amount", "type", "description", "user_id", "user_title", "user_avatar", "created_at", "org_id")
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        USER_ID_FIELD_NUMBER: _ClassVar[int]
        USER_TITLE_FIELD_NUMBER: _ClassVar[int]
        USER_AVATAR_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        ORG_ID_FIELD_NUMBER: _ClassVar[int]
        amount: int
        type: str
        description: str
        user_id: str
        user_title: str
        user_avatar: str
        created_at: _timestamp_pb2.Timestamp
        org_id: str
        def __init__(self, amount: _Optional[int] = ..., type: _Optional[str] = ..., description: _Optional[str] = ..., user_id: _Optional[str] = ..., user_title: _Optional[str] = ..., user_avatar: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., org_id: _Optional[str] = ...) -> None: ...
    ORGANIZATION_TOKENS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    organization_tokens: _containers.RepeatedCompositeFieldContainer[SearchOrganizationTokensResponse.OrganizationToken]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, organization_tokens: _Optional[_Iterable[_Union[SearchOrganizationTokensResponse.OrganizationToken, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class ExportOrganizationTokensRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class SearchOrganizationServiceUserCredentialsRequest(_message.Message):
    __slots__ = ("id", "query")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    query: _models_pb2.RQLRequest
    def __init__(self, id: _Optional[str] = ..., query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchOrganizationServiceUserCredentialsResponse(_message.Message):
    __slots__ = ("organization_serviceuser_credentials", "pagination", "group")
    class OrganizationServiceUserCredential(_message.Message):
        __slots__ = ("title", "serviceuser_title", "created_at", "org_id")
        TITLE_FIELD_NUMBER: _ClassVar[int]
        SERVICEUSER_TITLE_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        ORG_ID_FIELD_NUMBER: _ClassVar[int]
        title: str
        serviceuser_title: str
        created_at: _timestamp_pb2.Timestamp
        org_id: str
        def __init__(self, title: _Optional[str] = ..., serviceuser_title: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., org_id: _Optional[str] = ...) -> None: ...
    ORGANIZATION_SERVICEUSER_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    organization_serviceuser_credentials: _containers.RepeatedCompositeFieldContainer[SearchOrganizationServiceUserCredentialsResponse.OrganizationServiceUserCredential]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, organization_serviceuser_credentials: _Optional[_Iterable[_Union[SearchOrganizationServiceUserCredentialsResponse.OrganizationServiceUserCredential, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class SearchUsersRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: _models_pb2.RQLRequest
    def __init__(self, query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchUsersResponse(_message.Message):
    __slots__ = ("users", "pagination", "group")
    USERS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_models_pb2.User]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, users: _Optional[_Iterable[_Union[_models_pb2.User, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class ExportUsersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SearchUserOrganizationsRequest(_message.Message):
    __slots__ = ("id", "query")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    query: _models_pb2.RQLRequest
    def __init__(self, id: _Optional[str] = ..., query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchUserOrganizationsResponse(_message.Message):
    __slots__ = ("user_organizations", "pagination", "group")
    class UserOrganization(_message.Message):
        __slots__ = ("org_id", "org_title", "org_name", "org_avatar", "project_count", "role_names", "role_titles", "role_ids", "org_joined_on", "user_id")
        ORG_ID_FIELD_NUMBER: _ClassVar[int]
        ORG_TITLE_FIELD_NUMBER: _ClassVar[int]
        ORG_NAME_FIELD_NUMBER: _ClassVar[int]
        ORG_AVATAR_FIELD_NUMBER: _ClassVar[int]
        PROJECT_COUNT_FIELD_NUMBER: _ClassVar[int]
        ROLE_NAMES_FIELD_NUMBER: _ClassVar[int]
        ROLE_TITLES_FIELD_NUMBER: _ClassVar[int]
        ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
        ORG_JOINED_ON_FIELD_NUMBER: _ClassVar[int]
        USER_ID_FIELD_NUMBER: _ClassVar[int]
        org_id: str
        org_title: str
        org_name: str
        org_avatar: str
        project_count: int
        role_names: _containers.RepeatedScalarFieldContainer[str]
        role_titles: _containers.RepeatedScalarFieldContainer[str]
        role_ids: _containers.RepeatedScalarFieldContainer[str]
        org_joined_on: _timestamp_pb2.Timestamp
        user_id: str
        def __init__(self, org_id: _Optional[str] = ..., org_title: _Optional[str] = ..., org_name: _Optional[str] = ..., org_avatar: _Optional[str] = ..., project_count: _Optional[int] = ..., role_names: _Optional[_Iterable[str]] = ..., role_titles: _Optional[_Iterable[str]] = ..., role_ids: _Optional[_Iterable[str]] = ..., org_joined_on: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., user_id: _Optional[str] = ...) -> None: ...
    USER_ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    user_organizations: _containers.RepeatedCompositeFieldContainer[SearchUserOrganizationsResponse.UserOrganization]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, user_organizations: _Optional[_Iterable[_Union[SearchUserOrganizationsResponse.UserOrganization, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class SearchUserProjectsRequest(_message.Message):
    __slots__ = ("user_id", "org_id", "query")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    org_id: str
    query: _models_pb2.RQLRequest
    def __init__(self, user_id: _Optional[str] = ..., org_id: _Optional[str] = ..., query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchUserProjectsResponse(_message.Message):
    __slots__ = ("user_projects", "pagination", "group")
    class UserProject(_message.Message):
        __slots__ = ("project_id", "project_title", "project_name", "project_created_on", "user_names", "user_titles", "user_ids", "user_avatars", "org_id", "user_id")
        PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
        PROJECT_TITLE_FIELD_NUMBER: _ClassVar[int]
        PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
        PROJECT_CREATED_ON_FIELD_NUMBER: _ClassVar[int]
        USER_NAMES_FIELD_NUMBER: _ClassVar[int]
        USER_TITLES_FIELD_NUMBER: _ClassVar[int]
        USER_IDS_FIELD_NUMBER: _ClassVar[int]
        USER_AVATARS_FIELD_NUMBER: _ClassVar[int]
        ORG_ID_FIELD_NUMBER: _ClassVar[int]
        USER_ID_FIELD_NUMBER: _ClassVar[int]
        project_id: str
        project_title: str
        project_name: str
        project_created_on: _timestamp_pb2.Timestamp
        user_names: _containers.RepeatedScalarFieldContainer[str]
        user_titles: _containers.RepeatedScalarFieldContainer[str]
        user_ids: _containers.RepeatedScalarFieldContainer[str]
        user_avatars: _containers.RepeatedScalarFieldContainer[str]
        org_id: str
        user_id: str
        def __init__(self, project_id: _Optional[str] = ..., project_title: _Optional[str] = ..., project_name: _Optional[str] = ..., project_created_on: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., user_names: _Optional[_Iterable[str]] = ..., user_titles: _Optional[_Iterable[str]] = ..., user_ids: _Optional[_Iterable[str]] = ..., user_avatars: _Optional[_Iterable[str]] = ..., org_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...
    USER_PROJECTS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    user_projects: _containers.RepeatedCompositeFieldContainer[SearchUserProjectsResponse.UserProject]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, user_projects: _Optional[_Iterable[_Union[SearchUserProjectsResponse.UserProject, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class AdminCreateOrganizationRequest(_message.Message):
    __slots__ = ("body",)
    class OrganizationRequestBody(_message.Message):
        __slots__ = ("name", "title", "metadata", "avatar", "org_owner_email")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        METADATA_FIELD_NUMBER: _ClassVar[int]
        AVATAR_FIELD_NUMBER: _ClassVar[int]
        ORG_OWNER_EMAIL_FIELD_NUMBER: _ClassVar[int]
        name: str
        title: str
        metadata: _struct_pb2.Struct
        avatar: str
        org_owner_email: str
        def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., avatar: _Optional[str] = ..., org_owner_email: _Optional[str] = ...) -> None: ...
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: AdminCreateOrganizationRequest.OrganizationRequestBody
    def __init__(self, body: _Optional[_Union[AdminCreateOrganizationRequest.OrganizationRequestBody, _Mapping]] = ...) -> None: ...

class AdminCreateOrganizationResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: _models_pb2.Organization
    def __init__(self, organization: _Optional[_Union[_models_pb2.Organization, _Mapping]] = ...) -> None: ...

class SearchInvoicesRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: _models_pb2.RQLRequest
    def __init__(self, query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchInvoicesResponse(_message.Message):
    __slots__ = ("invoices", "pagination", "group")
    class Invoice(_message.Message):
        __slots__ = ("id", "amount", "currency", "state", "invoice_link", "created_at", "org_id", "org_name", "org_title")
        ID_FIELD_NUMBER: _ClassVar[int]
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        CURRENCY_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        INVOICE_LINK_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        ORG_ID_FIELD_NUMBER: _ClassVar[int]
        ORG_NAME_FIELD_NUMBER: _ClassVar[int]
        ORG_TITLE_FIELD_NUMBER: _ClassVar[int]
        id: str
        amount: int
        currency: str
        state: str
        invoice_link: str
        created_at: _timestamp_pb2.Timestamp
        org_id: str
        org_name: str
        org_title: str
        def __init__(self, id: _Optional[str] = ..., amount: _Optional[int] = ..., currency: _Optional[str] = ..., state: _Optional[str] = ..., invoice_link: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., org_id: _Optional[str] = ..., org_name: _Optional[str] = ..., org_title: _Optional[str] = ...) -> None: ...
    INVOICES_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    invoices: _containers.RepeatedCompositeFieldContainer[SearchInvoicesResponse.Invoice]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, invoices: _Optional[_Iterable[_Union[SearchInvoicesResponse.Invoice, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class SearchOrganizationServiceUsersRequest(_message.Message):
    __slots__ = ("id", "query")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    id: str
    query: _models_pb2.RQLRequest
    def __init__(self, id: _Optional[str] = ..., query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class SearchOrganizationServiceUsersResponse(_message.Message):
    __slots__ = ("organization_service_users", "pagination", "group")
    class Project(_message.Message):
        __slots__ = ("id", "title", "name")
        ID_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        id: str
        title: str
        name: str
        def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...
    class OrganizationServiceUser(_message.Message):
        __slots__ = ("id", "title", "org_id", "projects", "created_at")
        ID_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        ORG_ID_FIELD_NUMBER: _ClassVar[int]
        PROJECTS_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        id: str
        title: str
        org_id: str
        projects: _containers.RepeatedCompositeFieldContainer[SearchOrganizationServiceUsersResponse.Project]
        created_at: _timestamp_pb2.Timestamp
        def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., org_id: _Optional[str] = ..., projects: _Optional[_Iterable[_Union[SearchOrganizationServiceUsersResponse.Project, _Mapping]]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    ORGANIZATION_SERVICE_USERS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    organization_service_users: _containers.RepeatedCompositeFieldContainer[SearchOrganizationServiceUsersResponse.OrganizationServiceUser]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, organization_service_users: _Optional[_Iterable[_Union[SearchOrganizationServiceUsersResponse.OrganizationServiceUser, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...

class GetCurrentAdminUserRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCurrentAdminUserResponse(_message.Message):
    __slots__ = ("user", "service_user")
    USER_FIELD_NUMBER: _ClassVar[int]
    SERVICE_USER_FIELD_NUMBER: _ClassVar[int]
    user: _models_pb2.User
    service_user: _models_pb2.ServiceUser
    def __init__(self, user: _Optional[_Union[_models_pb2.User, _Mapping]] = ..., service_user: _Optional[_Union[_models_pb2.ServiceUser, _Mapping]] = ...) -> None: ...

class ListUserSessionsRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class ListUserSessionsResponse(_message.Message):
    __slots__ = ("sessions",)
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedCompositeFieldContainer[_models_pb2.Session]
    def __init__(self, sessions: _Optional[_Iterable[_Union[_models_pb2.Session, _Mapping]]] = ...) -> None: ...

class RevokeUserSessionRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class RevokeUserSessionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListAuditRecordsRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: _models_pb2.RQLRequest
    def __init__(self, query: _Optional[_Union[_models_pb2.RQLRequest, _Mapping]] = ...) -> None: ...

class ExportAuditRecordsRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: _models_pb2.RQLExportRequest
    def __init__(self, query: _Optional[_Union[_models_pb2.RQLExportRequest, _Mapping]] = ...) -> None: ...

class ListAuditRecordsResponse(_message.Message):
    __slots__ = ("audit_records", "pagination", "group")
    AUDIT_RECORDS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    audit_records: _containers.RepeatedCompositeFieldContainer[_models_pb2.AuditRecord]
    pagination: _models_pb2.RQLQueryPaginationResponse
    group: _models_pb2.RQLQueryGroupResponse
    def __init__(self, audit_records: _Optional[_Iterable[_Union[_models_pb2.AuditRecord, _Mapping]]] = ..., pagination: _Optional[_Union[_models_pb2.RQLQueryPaginationResponse, _Mapping]] = ..., group: _Optional[_Union[_models_pb2.RQLQueryGroupResponse, _Mapping]] = ...) -> None: ...
