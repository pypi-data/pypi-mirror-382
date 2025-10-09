import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from raystack.frontier.v1beta1 import models_pb2 as _models_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BillingAccountRequestBody(_message.Message):
    __slots__ = ("name", "email", "phone", "address", "currency", "tax_data", "metadata")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    TAX_DATA_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    email: str
    phone: str
    address: _models_pb2.BillingAccount.Address
    currency: str
    tax_data: _containers.RepeatedCompositeFieldContainer[_models_pb2.BillingAccount.Tax]
    metadata: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., address: _Optional[_Union[_models_pb2.BillingAccount.Address, _Mapping]] = ..., currency: _Optional[str] = ..., tax_data: _Optional[_Iterable[_Union[_models_pb2.BillingAccount.Tax, _Mapping]]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateBillingAccountRequest(_message.Message):
    __slots__ = ("org_id", "body", "offline")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    body: BillingAccountRequestBody
    offline: bool
    def __init__(self, org_id: _Optional[str] = ..., body: _Optional[_Union[BillingAccountRequestBody, _Mapping]] = ..., offline: _Optional[bool] = ...) -> None: ...

class CreateBillingAccountResponse(_message.Message):
    __slots__ = ("billing_account",)
    BILLING_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    billing_account: _models_pb2.BillingAccount
    def __init__(self, billing_account: _Optional[_Union[_models_pb2.BillingAccount, _Mapping]] = ...) -> None: ...

class GetBillingAccountRequest(_message.Message):
    __slots__ = ("id", "org_id", "with_payment_methods", "with_billing_details", "expand")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    WITH_PAYMENT_METHODS_FIELD_NUMBER: _ClassVar[int]
    WITH_BILLING_DETAILS_FIELD_NUMBER: _ClassVar[int]
    EXPAND_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    with_payment_methods: bool
    with_billing_details: bool
    expand: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., with_payment_methods: _Optional[bool] = ..., with_billing_details: _Optional[bool] = ..., expand: _Optional[_Iterable[str]] = ...) -> None: ...

class GetBillingAccountResponse(_message.Message):
    __slots__ = ("billing_account", "payment_methods", "billing_details")
    BILLING_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_METHODS_FIELD_NUMBER: _ClassVar[int]
    BILLING_DETAILS_FIELD_NUMBER: _ClassVar[int]
    billing_account: _models_pb2.BillingAccount
    payment_methods: _containers.RepeatedCompositeFieldContainer[_models_pb2.PaymentMethod]
    billing_details: _models_pb2.BillingAccountDetails
    def __init__(self, billing_account: _Optional[_Union[_models_pb2.BillingAccount, _Mapping]] = ..., payment_methods: _Optional[_Iterable[_Union[_models_pb2.PaymentMethod, _Mapping]]] = ..., billing_details: _Optional[_Union[_models_pb2.BillingAccountDetails, _Mapping]] = ...) -> None: ...

class UpdateBillingAccountRequest(_message.Message):
    __slots__ = ("id", "org_id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    body: BillingAccountRequestBody
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., body: _Optional[_Union[BillingAccountRequestBody, _Mapping]] = ...) -> None: ...

class UpdateBillingAccountResponse(_message.Message):
    __slots__ = ("billing_account",)
    BILLING_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    billing_account: _models_pb2.BillingAccount
    def __init__(self, billing_account: _Optional[_Union[_models_pb2.BillingAccount, _Mapping]] = ...) -> None: ...

class RegisterBillingAccountRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class RegisterBillingAccountResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListBillingAccountsRequest(_message.Message):
    __slots__ = ("org_id", "expand")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    EXPAND_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    expand: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, org_id: _Optional[str] = ..., expand: _Optional[_Iterable[str]] = ...) -> None: ...

class ListBillingAccountsResponse(_message.Message):
    __slots__ = ("billing_accounts",)
    BILLING_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    billing_accounts: _containers.RepeatedCompositeFieldContainer[_models_pb2.BillingAccount]
    def __init__(self, billing_accounts: _Optional[_Iterable[_Union[_models_pb2.BillingAccount, _Mapping]]] = ...) -> None: ...

class DeleteBillingAccountRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DeleteBillingAccountResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EnableBillingAccountRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class EnableBillingAccountResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DisableBillingAccountRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DisableBillingAccountResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetBillingBalanceRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class GetBillingBalanceResponse(_message.Message):
    __slots__ = ("balance",)
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    balance: _models_pb2.BillingAccount.Balance
    def __init__(self, balance: _Optional[_Union[_models_pb2.BillingAccount.Balance, _Mapping]] = ...) -> None: ...

class HasTrialedRequest(_message.Message):
    __slots__ = ("id", "org_id", "plan_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    plan_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., plan_id: _Optional[str] = ...) -> None: ...

class HasTrialedResponse(_message.Message):
    __slots__ = ("trialed",)
    TRIALED_FIELD_NUMBER: _ClassVar[int]
    trialed: bool
    def __init__(self, trialed: _Optional[bool] = ...) -> None: ...

class CreateBillingUsageRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "project_id", "usages")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    USAGES_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    project_id: str
    usages: _containers.RepeatedCompositeFieldContainer[_models_pb2.Usage]
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., project_id: _Optional[str] = ..., usages: _Optional[_Iterable[_Union[_models_pb2.Usage, _Mapping]]] = ...) -> None: ...

class CreateBillingUsageResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListBillingTransactionsRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "since", "start_range", "end_range", "expand")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    SINCE_FIELD_NUMBER: _ClassVar[int]
    START_RANGE_FIELD_NUMBER: _ClassVar[int]
    END_RANGE_FIELD_NUMBER: _ClassVar[int]
    EXPAND_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    since: _timestamp_pb2.Timestamp
    start_range: _timestamp_pb2.Timestamp
    end_range: _timestamp_pb2.Timestamp
    expand: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., since: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., start_range: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_range: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expand: _Optional[_Iterable[str]] = ...) -> None: ...

class ListBillingTransactionsResponse(_message.Message):
    __slots__ = ("transactions",)
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    transactions: _containers.RepeatedCompositeFieldContainer[_models_pb2.BillingTransaction]
    def __init__(self, transactions: _Optional[_Iterable[_Union[_models_pb2.BillingTransaction, _Mapping]]] = ...) -> None: ...

class TotalDebitedTransactionsRequest(_message.Message):
    __slots__ = ("org_id", "billing_id")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ...) -> None: ...

class TotalDebitedTransactionsResponse(_message.Message):
    __slots__ = ("debited",)
    DEBITED_FIELD_NUMBER: _ClassVar[int]
    debited: _models_pb2.BillingAccount.Balance
    def __init__(self, debited: _Optional[_Union[_models_pb2.BillingAccount.Balance, _Mapping]] = ...) -> None: ...

class GetSubscriptionRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "id", "expand")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPAND_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    id: str
    expand: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., id: _Optional[str] = ..., expand: _Optional[_Iterable[str]] = ...) -> None: ...

class GetSubscriptionResponse(_message.Message):
    __slots__ = ("subscription",)
    SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    subscription: _models_pb2.Subscription
    def __init__(self, subscription: _Optional[_Union[_models_pb2.Subscription, _Mapping]] = ...) -> None: ...

class ListSubscriptionsRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "state", "plan", "expand")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PLAN_FIELD_NUMBER: _ClassVar[int]
    EXPAND_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    state: str
    plan: str
    expand: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., state: _Optional[str] = ..., plan: _Optional[str] = ..., expand: _Optional[_Iterable[str]] = ...) -> None: ...

class ListSubscriptionsResponse(_message.Message):
    __slots__ = ("subscriptions",)
    SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    subscriptions: _containers.RepeatedCompositeFieldContainer[_models_pb2.Subscription]
    def __init__(self, subscriptions: _Optional[_Iterable[_Union[_models_pb2.Subscription, _Mapping]]] = ...) -> None: ...

class UpdateSubscriptionRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "id", "metadata")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    id: str
    metadata: _struct_pb2.Struct
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdateSubscriptionResponse(_message.Message):
    __slots__ = ("subscription",)
    SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    subscription: _models_pb2.Subscription
    def __init__(self, subscription: _Optional[_Union[_models_pb2.Subscription, _Mapping]] = ...) -> None: ...

class ChangeSubscriptionRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "id", "plan", "immediate", "plan_change", "phase_change")
    class PlanChange(_message.Message):
        __slots__ = ("plan", "immediate")
        PLAN_FIELD_NUMBER: _ClassVar[int]
        IMMEDIATE_FIELD_NUMBER: _ClassVar[int]
        plan: str
        immediate: bool
        def __init__(self, plan: _Optional[str] = ..., immediate: _Optional[bool] = ...) -> None: ...
    class PhaseChange(_message.Message):
        __slots__ = ("cancel_upcoming_changes",)
        CANCEL_UPCOMING_CHANGES_FIELD_NUMBER: _ClassVar[int]
        cancel_upcoming_changes: bool
        def __init__(self, cancel_upcoming_changes: _Optional[bool] = ...) -> None: ...
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PLAN_FIELD_NUMBER: _ClassVar[int]
    IMMEDIATE_FIELD_NUMBER: _ClassVar[int]
    PLAN_CHANGE_FIELD_NUMBER: _ClassVar[int]
    PHASE_CHANGE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    id: str
    plan: str
    immediate: bool
    plan_change: ChangeSubscriptionRequest.PlanChange
    phase_change: ChangeSubscriptionRequest.PhaseChange
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., id: _Optional[str] = ..., plan: _Optional[str] = ..., immediate: _Optional[bool] = ..., plan_change: _Optional[_Union[ChangeSubscriptionRequest.PlanChange, _Mapping]] = ..., phase_change: _Optional[_Union[ChangeSubscriptionRequest.PhaseChange, _Mapping]] = ...) -> None: ...

class ChangeSubscriptionResponse(_message.Message):
    __slots__ = ("phase",)
    PHASE_FIELD_NUMBER: _ClassVar[int]
    phase: _models_pb2.Subscription.Phase
    def __init__(self, phase: _Optional[_Union[_models_pb2.Subscription.Phase, _Mapping]] = ...) -> None: ...

class CancelSubscriptionRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "id", "immediate")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IMMEDIATE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    id: str
    immediate: bool
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., id: _Optional[str] = ..., immediate: _Optional[bool] = ...) -> None: ...

class CancelSubscriptionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPlansRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPlansResponse(_message.Message):
    __slots__ = ("plans",)
    PLANS_FIELD_NUMBER: _ClassVar[int]
    plans: _containers.RepeatedCompositeFieldContainer[_models_pb2.Plan]
    def __init__(self, plans: _Optional[_Iterable[_Union[_models_pb2.Plan, _Mapping]]] = ...) -> None: ...

class CheckFeatureEntitlementRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "project_id", "feature")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    project_id: str
    feature: str
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., project_id: _Optional[str] = ..., feature: _Optional[str] = ...) -> None: ...

class CheckFeatureEntitlementResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: _Optional[bool] = ...) -> None: ...

class CheckCreditEntitlementRequest(_message.Message):
    __slots__ = ("org_id", "amount")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    amount: int
    def __init__(self, org_id: _Optional[str] = ..., amount: _Optional[int] = ...) -> None: ...

class CheckCreditEntitlementResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: _Optional[bool] = ...) -> None: ...

class CreateCheckoutRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "success_url", "cancel_url", "subscription_body", "product_body", "setup_body")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_URL_FIELD_NUMBER: _ClassVar[int]
    CANCEL_URL_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_BODY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_BODY_FIELD_NUMBER: _ClassVar[int]
    SETUP_BODY_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    success_url: str
    cancel_url: str
    subscription_body: _models_pb2.CheckoutSubscriptionBody
    product_body: _models_pb2.CheckoutProductBody
    setup_body: _models_pb2.CheckoutSetupBody
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., success_url: _Optional[str] = ..., cancel_url: _Optional[str] = ..., subscription_body: _Optional[_Union[_models_pb2.CheckoutSubscriptionBody, _Mapping]] = ..., product_body: _Optional[_Union[_models_pb2.CheckoutProductBody, _Mapping]] = ..., setup_body: _Optional[_Union[_models_pb2.CheckoutSetupBody, _Mapping]] = ...) -> None: ...

class CreateCheckoutResponse(_message.Message):
    __slots__ = ("checkout_session",)
    CHECKOUT_SESSION_FIELD_NUMBER: _ClassVar[int]
    checkout_session: _models_pb2.CheckoutSession
    def __init__(self, checkout_session: _Optional[_Union[_models_pb2.CheckoutSession, _Mapping]] = ...) -> None: ...

class ListCheckoutsRequest(_message.Message):
    __slots__ = ("org_id", "billing_id")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ...) -> None: ...

class ListCheckoutsResponse(_message.Message):
    __slots__ = ("checkout_sessions",)
    CHECKOUT_SESSIONS_FIELD_NUMBER: _ClassVar[int]
    checkout_sessions: _containers.RepeatedCompositeFieldContainer[_models_pb2.CheckoutSession]
    def __init__(self, checkout_sessions: _Optional[_Iterable[_Union[_models_pb2.CheckoutSession, _Mapping]]] = ...) -> None: ...

class GetCheckoutRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "id")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    id: str
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class GetCheckoutResponse(_message.Message):
    __slots__ = ("checkout_session",)
    CHECKOUT_SESSION_FIELD_NUMBER: _ClassVar[int]
    checkout_session: _models_pb2.CheckoutSession
    def __init__(self, checkout_session: _Optional[_Union[_models_pb2.CheckoutSession, _Mapping]] = ...) -> None: ...

class ProductRequestBody(_message.Message):
    __slots__ = ("name", "title", "description", "plan_id", "prices", "behavior", "features", "behavior_config", "metadata")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    PRICES_FIELD_NUMBER: _ClassVar[int]
    BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    BEHAVIOR_CONFIG_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    title: str
    description: str
    plan_id: str
    prices: _containers.RepeatedCompositeFieldContainer[_models_pb2.Price]
    behavior: str
    features: _containers.RepeatedCompositeFieldContainer[_models_pb2.Feature]
    behavior_config: _models_pb2.Product.BehaviorConfig
    metadata: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., plan_id: _Optional[str] = ..., prices: _Optional[_Iterable[_Union[_models_pb2.Price, _Mapping]]] = ..., behavior: _Optional[str] = ..., features: _Optional[_Iterable[_Union[_models_pb2.Feature, _Mapping]]] = ..., behavior_config: _Optional[_Union[_models_pb2.Product.BehaviorConfig, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateProductRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: ProductRequestBody
    def __init__(self, body: _Optional[_Union[ProductRequestBody, _Mapping]] = ...) -> None: ...

class CreateProductResponse(_message.Message):
    __slots__ = ("product",)
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: _models_pb2.Product
    def __init__(self, product: _Optional[_Union[_models_pb2.Product, _Mapping]] = ...) -> None: ...

class GetProductRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetProductResponse(_message.Message):
    __slots__ = ("product",)
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: _models_pb2.Product
    def __init__(self, product: _Optional[_Union[_models_pb2.Product, _Mapping]] = ...) -> None: ...

class ListProductsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListProductsResponse(_message.Message):
    __slots__ = ("products",)
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[_models_pb2.Product]
    def __init__(self, products: _Optional[_Iterable[_Union[_models_pb2.Product, _Mapping]]] = ...) -> None: ...

class UpdateProductRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: ProductRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[ProductRequestBody, _Mapping]] = ...) -> None: ...

class UpdateProductResponse(_message.Message):
    __slots__ = ("product",)
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: _models_pb2.Product
    def __init__(self, product: _Optional[_Union[_models_pb2.Product, _Mapping]] = ...) -> None: ...

class FeatureRequestBody(_message.Message):
    __slots__ = ("name", "title", "product_ids", "metadata")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    title: str
    product_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., product_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateFeatureRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: FeatureRequestBody
    def __init__(self, body: _Optional[_Union[FeatureRequestBody, _Mapping]] = ...) -> None: ...

class CreateFeatureResponse(_message.Message):
    __slots__ = ("feature",)
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    feature: _models_pb2.Feature
    def __init__(self, feature: _Optional[_Union[_models_pb2.Feature, _Mapping]] = ...) -> None: ...

class GetFeatureRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetFeatureResponse(_message.Message):
    __slots__ = ("feature",)
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    feature: _models_pb2.Feature
    def __init__(self, feature: _Optional[_Union[_models_pb2.Feature, _Mapping]] = ...) -> None: ...

class UpdateFeatureRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: FeatureRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[FeatureRequestBody, _Mapping]] = ...) -> None: ...

class UpdateFeatureResponse(_message.Message):
    __slots__ = ("feature",)
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    feature: _models_pb2.Feature
    def __init__(self, feature: _Optional[_Union[_models_pb2.Feature, _Mapping]] = ...) -> None: ...

class ListFeaturesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListFeaturesResponse(_message.Message):
    __slots__ = ("features",)
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    features: _containers.RepeatedCompositeFieldContainer[_models_pb2.Feature]
    def __init__(self, features: _Optional[_Iterable[_Union[_models_pb2.Feature, _Mapping]]] = ...) -> None: ...

class PlanRequestBody(_message.Message):
    __slots__ = ("name", "title", "description", "products", "interval", "on_start_credits", "trial_days", "metadata")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    ON_START_CREDITS_FIELD_NUMBER: _ClassVar[int]
    TRIAL_DAYS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    title: str
    description: str
    products: _containers.RepeatedCompositeFieldContainer[_models_pb2.Product]
    interval: str
    on_start_credits: int
    trial_days: int
    metadata: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., products: _Optional[_Iterable[_Union[_models_pb2.Product, _Mapping]]] = ..., interval: _Optional[str] = ..., on_start_credits: _Optional[int] = ..., trial_days: _Optional[int] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreatePlanRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: PlanRequestBody
    def __init__(self, body: _Optional[_Union[PlanRequestBody, _Mapping]] = ...) -> None: ...

class CreatePlanResponse(_message.Message):
    __slots__ = ("plan",)
    PLAN_FIELD_NUMBER: _ClassVar[int]
    plan: _models_pb2.Plan
    def __init__(self, plan: _Optional[_Union[_models_pb2.Plan, _Mapping]] = ...) -> None: ...

class GetPlanRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetPlanResponse(_message.Message):
    __slots__ = ("plan",)
    PLAN_FIELD_NUMBER: _ClassVar[int]
    plan: _models_pb2.Plan
    def __init__(self, plan: _Optional[_Union[_models_pb2.Plan, _Mapping]] = ...) -> None: ...

class UpdatePlanRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: PlanRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[PlanRequestBody, _Mapping]] = ...) -> None: ...

class UpdatePlanResponse(_message.Message):
    __slots__ = ("plan",)
    PLAN_FIELD_NUMBER: _ClassVar[int]
    plan: _models_pb2.Plan
    def __init__(self, plan: _Optional[_Union[_models_pb2.Plan, _Mapping]] = ...) -> None: ...

class ListInvoicesRequest(_message.Message):
    __slots__ = ("org_id", "billing_id", "nonzero_amount_only", "expand")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    NONZERO_AMOUNT_ONLY_FIELD_NUMBER: _ClassVar[int]
    EXPAND_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    nonzero_amount_only: bool
    expand: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ..., nonzero_amount_only: _Optional[bool] = ..., expand: _Optional[_Iterable[str]] = ...) -> None: ...

class ListInvoicesResponse(_message.Message):
    __slots__ = ("invoices",)
    INVOICES_FIELD_NUMBER: _ClassVar[int]
    invoices: _containers.RepeatedCompositeFieldContainer[_models_pb2.Invoice]
    def __init__(self, invoices: _Optional[_Iterable[_Union[_models_pb2.Invoice, _Mapping]]] = ...) -> None: ...

class GetUpcomingInvoiceRequest(_message.Message):
    __slots__ = ("org_id", "billing_id")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    billing_id: str
    def __init__(self, org_id: _Optional[str] = ..., billing_id: _Optional[str] = ...) -> None: ...

class GetUpcomingInvoiceResponse(_message.Message):
    __slots__ = ("invoice",)
    INVOICE_FIELD_NUMBER: _ClassVar[int]
    invoice: _models_pb2.Invoice
    def __init__(self, invoice: _Optional[_Union[_models_pb2.Invoice, _Mapping]] = ...) -> None: ...

class GetJWKsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetJWKsResponse(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[_models_pb2.JSONWebKey]
    def __init__(self, keys: _Optional[_Iterable[_Union[_models_pb2.JSONWebKey, _Mapping]]] = ...) -> None: ...

class AuthLogoutRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AuthLogoutResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AuthCallbackRequest(_message.Message):
    __slots__ = ("strategy_name", "state", "code", "state_options")
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    STATE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    strategy_name: str
    state: str
    code: str
    state_options: _struct_pb2.Struct
    def __init__(self, strategy_name: _Optional[str] = ..., state: _Optional[str] = ..., code: _Optional[str] = ..., state_options: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class AuthCallbackResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AuthenticateRequest(_message.Message):
    __slots__ = ("strategy_name", "redirect_onstart", "return_to", "email", "callback_url")
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_ONSTART_FIELD_NUMBER: _ClassVar[int]
    RETURN_TO_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    CALLBACK_URL_FIELD_NUMBER: _ClassVar[int]
    strategy_name: str
    redirect_onstart: bool
    return_to: str
    email: str
    callback_url: str
    def __init__(self, strategy_name: _Optional[str] = ..., redirect_onstart: _Optional[bool] = ..., return_to: _Optional[str] = ..., email: _Optional[str] = ..., callback_url: _Optional[str] = ...) -> None: ...

class AuthenticateResponse(_message.Message):
    __slots__ = ("endpoint", "state", "state_options")
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    endpoint: str
    state: str
    state_options: _struct_pb2.Struct
    def __init__(self, endpoint: _Optional[str] = ..., state: _Optional[str] = ..., state_options: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class AuthStrategy(_message.Message):
    __slots__ = ("name", "params")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    name: str
    params: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., params: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class ListAuthStrategiesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListAuthStrategiesResponse(_message.Message):
    __slots__ = ("strategies",)
    STRATEGIES_FIELD_NUMBER: _ClassVar[int]
    strategies: _containers.RepeatedCompositeFieldContainer[AuthStrategy]
    def __init__(self, strategies: _Optional[_Iterable[_Union[AuthStrategy, _Mapping]]] = ...) -> None: ...

class AuthTokenRequest(_message.Message):
    __slots__ = ("grant_type", "client_id", "client_secret", "assertion")
    GRANT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    ASSERTION_FIELD_NUMBER: _ClassVar[int]
    grant_type: str
    client_id: str
    client_secret: str
    assertion: str
    def __init__(self, grant_type: _Optional[str] = ..., client_id: _Optional[str] = ..., client_secret: _Optional[str] = ..., assertion: _Optional[str] = ...) -> None: ...

class AuthTokenResponse(_message.Message):
    __slots__ = ("access_token", "token_type")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    token_type: str
    def __init__(self, access_token: _Optional[str] = ..., token_type: _Optional[str] = ...) -> None: ...

class UserRequestBody(_message.Message):
    __slots__ = ("name", "email", "metadata", "title", "avatar")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    name: str
    email: str
    metadata: _struct_pb2.Struct
    title: str
    avatar: str
    def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., title: _Optional[str] = ..., avatar: _Optional[str] = ...) -> None: ...

class ListUsersRequest(_message.Message):
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

class ListUsersResponse(_message.Message):
    __slots__ = ("count", "users")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    count: int
    users: _containers.RepeatedCompositeFieldContainer[_models_pb2.User]
    def __init__(self, count: _Optional[int] = ..., users: _Optional[_Iterable[_Union[_models_pb2.User, _Mapping]]] = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: UserRequestBody
    def __init__(self, body: _Optional[_Union[UserRequestBody, _Mapping]] = ...) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _models_pb2.User
    def __init__(self, user: _Optional[_Union[_models_pb2.User, _Mapping]] = ...) -> None: ...

class ListOrganizationsByUserRequest(_message.Message):
    __slots__ = ("id", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: str
    def __init__(self, id: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class ListOrganizationsByUserResponse(_message.Message):
    __slots__ = ("organizations", "joinable_via_domain")
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    JOINABLE_VIA_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Organization]
    joinable_via_domain: _containers.RepeatedCompositeFieldContainer[_models_pb2.Organization]
    def __init__(self, organizations: _Optional[_Iterable[_Union[_models_pb2.Organization, _Mapping]]] = ..., joinable_via_domain: _Optional[_Iterable[_Union[_models_pb2.Organization, _Mapping]]] = ...) -> None: ...

class ListOrganizationsByCurrentUserRequest(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: str
    def __init__(self, state: _Optional[str] = ...) -> None: ...

class ListOrganizationsByCurrentUserResponse(_message.Message):
    __slots__ = ("organizations", "joinable_via_domain")
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    JOINABLE_VIA_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Organization]
    joinable_via_domain: _containers.RepeatedCompositeFieldContainer[_models_pb2.Organization]
    def __init__(self, organizations: _Optional[_Iterable[_Union[_models_pb2.Organization, _Mapping]]] = ..., joinable_via_domain: _Optional[_Iterable[_Union[_models_pb2.Organization, _Mapping]]] = ...) -> None: ...

class ListProjectsByUserRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListProjectsByUserResponse(_message.Message):
    __slots__ = ("projects",)
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[_models_pb2.Project]
    def __init__(self, projects: _Optional[_Iterable[_Union[_models_pb2.Project, _Mapping]]] = ...) -> None: ...

class ListProjectsByCurrentUserRequest(_message.Message):
    __slots__ = ("org_id", "with_permissions", "non_inherited", "with_member_count", "page_size", "page_num")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    WITH_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    NON_INHERITED_FIELD_NUMBER: _ClassVar[int]
    WITH_MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_NUM_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    with_permissions: _containers.RepeatedScalarFieldContainer[str]
    non_inherited: bool
    with_member_count: bool
    page_size: int
    page_num: int
    def __init__(self, org_id: _Optional[str] = ..., with_permissions: _Optional[_Iterable[str]] = ..., non_inherited: _Optional[bool] = ..., with_member_count: _Optional[bool] = ..., page_size: _Optional[int] = ..., page_num: _Optional[int] = ...) -> None: ...

class ListProjectsByCurrentUserResponse(_message.Message):
    __slots__ = ("projects", "access_pairs", "count")
    class AccessPair(_message.Message):
        __slots__ = ("project_id", "permissions")
        PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
        PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
        project_id: str
        permissions: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, project_id: _Optional[str] = ..., permissions: _Optional[_Iterable[str]] = ...) -> None: ...
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    ACCESS_PAIRS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[_models_pb2.Project]
    access_pairs: _containers.RepeatedCompositeFieldContainer[ListProjectsByCurrentUserResponse.AccessPair]
    count: int
    def __init__(self, projects: _Optional[_Iterable[_Union[_models_pb2.Project, _Mapping]]] = ..., access_pairs: _Optional[_Iterable[_Union[ListProjectsByCurrentUserResponse.AccessPair, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class EnableUserRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class EnableUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DisableUserRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DisableUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _models_pb2.User
    def __init__(self, user: _Optional[_Union[_models_pb2.User, _Mapping]] = ...) -> None: ...

class GetCurrentUserRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCurrentUserResponse(_message.Message):
    __slots__ = ("user", "serviceuser")
    USER_FIELD_NUMBER: _ClassVar[int]
    SERVICEUSER_FIELD_NUMBER: _ClassVar[int]
    user: _models_pb2.User
    serviceuser: _models_pb2.ServiceUser
    def __init__(self, user: _Optional[_Union[_models_pb2.User, _Mapping]] = ..., serviceuser: _Optional[_Union[_models_pb2.ServiceUser, _Mapping]] = ...) -> None: ...

class UpdateUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _models_pb2.User
    def __init__(self, user: _Optional[_Union[_models_pb2.User, _Mapping]] = ...) -> None: ...

class UpdateCurrentUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _models_pb2.User
    def __init__(self, user: _Optional[_Union[_models_pb2.User, _Mapping]] = ...) -> None: ...

class UpdateUserRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: UserRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[UserRequestBody, _Mapping]] = ...) -> None: ...

class GetUserRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListCurrentUserGroupsRequest(_message.Message):
    __slots__ = ("org_id", "with_permissions", "with_member_count")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    WITH_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    WITH_MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    with_permissions: _containers.RepeatedScalarFieldContainer[str]
    with_member_count: bool
    def __init__(self, org_id: _Optional[str] = ..., with_permissions: _Optional[_Iterable[str]] = ..., with_member_count: _Optional[bool] = ...) -> None: ...

class ListCurrentUserGroupsResponse(_message.Message):
    __slots__ = ("groups", "access_pairs")
    class AccessPair(_message.Message):
        __slots__ = ("group_id", "permissions")
        GROUP_ID_FIELD_NUMBER: _ClassVar[int]
        PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
        group_id: str
        permissions: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, group_id: _Optional[str] = ..., permissions: _Optional[_Iterable[str]] = ...) -> None: ...
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    ACCESS_PAIRS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_models_pb2.Group]
    access_pairs: _containers.RepeatedCompositeFieldContainer[ListCurrentUserGroupsResponse.AccessPair]
    def __init__(self, groups: _Optional[_Iterable[_Union[_models_pb2.Group, _Mapping]]] = ..., access_pairs: _Optional[_Iterable[_Union[ListCurrentUserGroupsResponse.AccessPair, _Mapping]]] = ...) -> None: ...

class ListUserGroupsRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class ListUserGroupsResponse(_message.Message):
    __slots__ = ("groups",)
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_models_pb2.Group]
    def __init__(self, groups: _Optional[_Iterable[_Union[_models_pb2.Group, _Mapping]]] = ...) -> None: ...

class UpdateCurrentUserRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: UserRequestBody
    def __init__(self, body: _Optional[_Union[UserRequestBody, _Mapping]] = ...) -> None: ...

class ListUserInvitationsRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListUserInvitationsResponse(_message.Message):
    __slots__ = ("invitations",)
    INVITATIONS_FIELD_NUMBER: _ClassVar[int]
    invitations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Invitation]
    def __init__(self, invitations: _Optional[_Iterable[_Union[_models_pb2.Invitation, _Mapping]]] = ...) -> None: ...

class ListCurrentUserInvitationsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListCurrentUserInvitationsResponse(_message.Message):
    __slots__ = ("invitations", "orgs")
    INVITATIONS_FIELD_NUMBER: _ClassVar[int]
    ORGS_FIELD_NUMBER: _ClassVar[int]
    invitations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Invitation]
    orgs: _containers.RepeatedCompositeFieldContainer[_models_pb2.Organization]
    def __init__(self, invitations: _Optional[_Iterable[_Union[_models_pb2.Invitation, _Mapping]]] = ..., orgs: _Optional[_Iterable[_Union[_models_pb2.Organization, _Mapping]]] = ...) -> None: ...

class ListServiceUsersRequest(_message.Message):
    __slots__ = ("org_id", "state")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    state: str
    def __init__(self, org_id: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class ListServiceUsersResponse(_message.Message):
    __slots__ = ("serviceusers",)
    SERVICEUSERS_FIELD_NUMBER: _ClassVar[int]
    serviceusers: _containers.RepeatedCompositeFieldContainer[_models_pb2.ServiceUser]
    def __init__(self, serviceusers: _Optional[_Iterable[_Union[_models_pb2.ServiceUser, _Mapping]]] = ...) -> None: ...

class ServiceUserRequestBody(_message.Message):
    __slots__ = ("title", "metadata")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    title: str
    metadata: _struct_pb2.Struct
    def __init__(self, title: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateServiceUserRequest(_message.Message):
    __slots__ = ("body", "org_id")
    BODY_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    body: ServiceUserRequestBody
    org_id: str
    def __init__(self, body: _Optional[_Union[ServiceUserRequestBody, _Mapping]] = ..., org_id: _Optional[str] = ...) -> None: ...

class CreateServiceUserResponse(_message.Message):
    __slots__ = ("serviceuser",)
    SERVICEUSER_FIELD_NUMBER: _ClassVar[int]
    serviceuser: _models_pb2.ServiceUser
    def __init__(self, serviceuser: _Optional[_Union[_models_pb2.ServiceUser, _Mapping]] = ...) -> None: ...

class GetServiceUserRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class GetServiceUserResponse(_message.Message):
    __slots__ = ("serviceuser",)
    SERVICEUSER_FIELD_NUMBER: _ClassVar[int]
    serviceuser: _models_pb2.ServiceUser
    def __init__(self, serviceuser: _Optional[_Union[_models_pb2.ServiceUser, _Mapping]] = ...) -> None: ...

class UpdateServiceUserRequest(_message.Message):
    __slots__ = ("id", "body", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: ServiceUserRequestBody
    org_id: str
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[ServiceUserRequestBody, _Mapping]] = ..., org_id: _Optional[str] = ...) -> None: ...

class UpdateServiceUserResponse(_message.Message):
    __slots__ = ("serviceuser",)
    SERVICEUSER_FIELD_NUMBER: _ClassVar[int]
    serviceuser: _models_pb2.ServiceUser
    def __init__(self, serviceuser: _Optional[_Union[_models_pb2.ServiceUser, _Mapping]] = ...) -> None: ...

class DeleteServiceUserRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DeleteServiceUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateServiceUserJWKRequest(_message.Message):
    __slots__ = ("id", "title", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class CreateServiceUserJWKResponse(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: _models_pb2.KeyCredential
    def __init__(self, key: _Optional[_Union[_models_pb2.KeyCredential, _Mapping]] = ...) -> None: ...

class GetServiceUserJWKRequest(_message.Message):
    __slots__ = ("id", "key_id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    key_id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., key_id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class GetServiceUserJWKResponse(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[_models_pb2.JSONWebKey]
    def __init__(self, keys: _Optional[_Iterable[_Union[_models_pb2.JSONWebKey, _Mapping]]] = ...) -> None: ...

class ListServiceUserJWKsRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class ListServiceUserJWKsResponse(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[_models_pb2.ServiceUserJWK]
    def __init__(self, keys: _Optional[_Iterable[_Union[_models_pb2.ServiceUserJWK, _Mapping]]] = ...) -> None: ...

class DeleteServiceUserJWKRequest(_message.Message):
    __slots__ = ("id", "key_id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    key_id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., key_id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DeleteServiceUserJWKResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateServiceUserCredentialRequest(_message.Message):
    __slots__ = ("id", "title", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class CreateServiceUserCredentialResponse(_message.Message):
    __slots__ = ("secret",)
    SECRET_FIELD_NUMBER: _ClassVar[int]
    secret: _models_pb2.SecretCredential
    def __init__(self, secret: _Optional[_Union[_models_pb2.SecretCredential, _Mapping]] = ...) -> None: ...

class ListServiceUserCredentialsRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class ListServiceUserCredentialsResponse(_message.Message):
    __slots__ = ("secrets",)
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    secrets: _containers.RepeatedCompositeFieldContainer[_models_pb2.SecretCredential]
    def __init__(self, secrets: _Optional[_Iterable[_Union[_models_pb2.SecretCredential, _Mapping]]] = ...) -> None: ...

class DeleteServiceUserCredentialRequest(_message.Message):
    __slots__ = ("id", "secret_id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    secret_id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., secret_id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DeleteServiceUserCredentialResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateServiceUserTokenRequest(_message.Message):
    __slots__ = ("id", "title", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class CreateServiceUserTokenResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: _models_pb2.ServiceUserToken
    def __init__(self, token: _Optional[_Union[_models_pb2.ServiceUserToken, _Mapping]] = ...) -> None: ...

class ListServiceUserTokensRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class ListServiceUserTokensResponse(_message.Message):
    __slots__ = ("tokens",)
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    tokens: _containers.RepeatedCompositeFieldContainer[_models_pb2.ServiceUserToken]
    def __init__(self, tokens: _Optional[_Iterable[_Union[_models_pb2.ServiceUserToken, _Mapping]]] = ...) -> None: ...

class DeleteServiceUserTokenRequest(_message.Message):
    __slots__ = ("id", "token_id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    token_id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., token_id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DeleteServiceUserTokenResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListServiceUserProjectsRequest(_message.Message):
    __slots__ = ("id", "org_id", "with_permissions")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    WITH_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    with_permissions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., with_permissions: _Optional[_Iterable[str]] = ...) -> None: ...

class ListServiceUserProjectsResponse(_message.Message):
    __slots__ = ("projects", "access_pairs")
    class AccessPair(_message.Message):
        __slots__ = ("project_id", "permissions")
        PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
        PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
        project_id: str
        permissions: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, project_id: _Optional[str] = ..., permissions: _Optional[_Iterable[str]] = ...) -> None: ...
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    ACCESS_PAIRS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[_models_pb2.Project]
    access_pairs: _containers.RepeatedCompositeFieldContainer[ListServiceUserProjectsResponse.AccessPair]
    def __init__(self, projects: _Optional[_Iterable[_Union[_models_pb2.Project, _Mapping]]] = ..., access_pairs: _Optional[_Iterable[_Union[ListServiceUserProjectsResponse.AccessPair, _Mapping]]] = ...) -> None: ...

class ListOrganizationGroupsRequest(_message.Message):
    __slots__ = ("org_id", "state", "group_ids", "with_members", "with_member_count")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    GROUP_IDS_FIELD_NUMBER: _ClassVar[int]
    WITH_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    WITH_MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    state: str
    group_ids: _containers.RepeatedScalarFieldContainer[str]
    with_members: bool
    with_member_count: bool
    def __init__(self, org_id: _Optional[str] = ..., state: _Optional[str] = ..., group_ids: _Optional[_Iterable[str]] = ..., with_members: _Optional[bool] = ..., with_member_count: _Optional[bool] = ...) -> None: ...

class ListOrganizationGroupsResponse(_message.Message):
    __slots__ = ("groups",)
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_models_pb2.Group]
    def __init__(self, groups: _Optional[_Iterable[_Union[_models_pb2.Group, _Mapping]]] = ...) -> None: ...

class CreateOrganizationRoleRequest(_message.Message):
    __slots__ = ("body", "org_id")
    BODY_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    body: _models_pb2.RoleRequestBody
    org_id: str
    def __init__(self, body: _Optional[_Union[_models_pb2.RoleRequestBody, _Mapping]] = ..., org_id: _Optional[str] = ...) -> None: ...

class CreateOrganizationRoleResponse(_message.Message):
    __slots__ = ("role",)
    ROLE_FIELD_NUMBER: _ClassVar[int]
    role: _models_pb2.Role
    def __init__(self, role: _Optional[_Union[_models_pb2.Role, _Mapping]] = ...) -> None: ...

class GetOrganizationRoleRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class GetOrganizationRoleResponse(_message.Message):
    __slots__ = ("role",)
    ROLE_FIELD_NUMBER: _ClassVar[int]
    role: _models_pb2.Role
    def __init__(self, role: _Optional[_Union[_models_pb2.Role, _Mapping]] = ...) -> None: ...

class UpdateOrganizationRoleRequest(_message.Message):
    __slots__ = ("id", "org_id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    body: _models_pb2.RoleRequestBody
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., body: _Optional[_Union[_models_pb2.RoleRequestBody, _Mapping]] = ...) -> None: ...

class UpdateOrganizationRoleResponse(_message.Message):
    __slots__ = ("role",)
    ROLE_FIELD_NUMBER: _ClassVar[int]
    role: _models_pb2.Role
    def __init__(self, role: _Optional[_Union[_models_pb2.Role, _Mapping]] = ...) -> None: ...

class ListRolesRequest(_message.Message):
    __slots__ = ("state", "scopes")
    STATE_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    state: str
    scopes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, state: _Optional[str] = ..., scopes: _Optional[_Iterable[str]] = ...) -> None: ...

class ListRolesResponse(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[_models_pb2.Role]
    def __init__(self, roles: _Optional[_Iterable[_Union[_models_pb2.Role, _Mapping]]] = ...) -> None: ...

class ListOrganizationRolesRequest(_message.Message):
    __slots__ = ("org_id", "state", "scopes")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    state: str
    scopes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, org_id: _Optional[str] = ..., state: _Optional[str] = ..., scopes: _Optional[_Iterable[str]] = ...) -> None: ...

class ListOrganizationRolesResponse(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[_models_pb2.Role]
    def __init__(self, roles: _Optional[_Iterable[_Union[_models_pb2.Role, _Mapping]]] = ...) -> None: ...

class DeleteOrganizationRoleRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DeleteOrganizationRoleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OrganizationRequestBody(_message.Message):
    __slots__ = ("name", "title", "metadata", "avatar")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    name: str
    title: str
    metadata: _struct_pb2.Struct
    avatar: str
    def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., avatar: _Optional[str] = ...) -> None: ...

class ListOrganizationsRequest(_message.Message):
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

class ListOrganizationsResponse(_message.Message):
    __slots__ = ("organizations",)
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Organization]
    def __init__(self, organizations: _Optional[_Iterable[_Union[_models_pb2.Organization, _Mapping]]] = ...) -> None: ...

class CreateOrganizationRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: OrganizationRequestBody
    def __init__(self, body: _Optional[_Union[OrganizationRequestBody, _Mapping]] = ...) -> None: ...

class CreateOrganizationResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: _models_pb2.Organization
    def __init__(self, organization: _Optional[_Union[_models_pb2.Organization, _Mapping]] = ...) -> None: ...

class GetOrganizationResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: _models_pb2.Organization
    def __init__(self, organization: _Optional[_Union[_models_pb2.Organization, _Mapping]] = ...) -> None: ...

class UpdateOrganizationResponse(_message.Message):
    __slots__ = ("organization",)
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    organization: _models_pb2.Organization
    def __init__(self, organization: _Optional[_Union[_models_pb2.Organization, _Mapping]] = ...) -> None: ...

class GetOrganizationRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class UpdateOrganizationRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: OrganizationRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[OrganizationRequestBody, _Mapping]] = ...) -> None: ...

class ListOrganizationAdminsRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListOrganizationAdminsResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_models_pb2.User]
    def __init__(self, users: _Optional[_Iterable[_Union[_models_pb2.User, _Mapping]]] = ...) -> None: ...

class ListOrganizationUsersRequest(_message.Message):
    __slots__ = ("id", "permission_filter", "with_roles", "role_filters")
    ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FILTER_FIELD_NUMBER: _ClassVar[int]
    WITH_ROLES_FIELD_NUMBER: _ClassVar[int]
    ROLE_FILTERS_FIELD_NUMBER: _ClassVar[int]
    id: str
    permission_filter: str
    with_roles: bool
    role_filters: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., permission_filter: _Optional[str] = ..., with_roles: _Optional[bool] = ..., role_filters: _Optional[_Iterable[str]] = ...) -> None: ...

class ListOrganizationUsersResponse(_message.Message):
    __slots__ = ("users", "role_pairs")
    class RolePair(_message.Message):
        __slots__ = ("user_id", "roles")
        USER_ID_FIELD_NUMBER: _ClassVar[int]
        ROLES_FIELD_NUMBER: _ClassVar[int]
        user_id: str
        roles: _containers.RepeatedCompositeFieldContainer[_models_pb2.Role]
        def __init__(self, user_id: _Optional[str] = ..., roles: _Optional[_Iterable[_Union[_models_pb2.Role, _Mapping]]] = ...) -> None: ...
    USERS_FIELD_NUMBER: _ClassVar[int]
    ROLE_PAIRS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_models_pb2.User]
    role_pairs: _containers.RepeatedCompositeFieldContainer[ListOrganizationUsersResponse.RolePair]
    def __init__(self, users: _Optional[_Iterable[_Union[_models_pb2.User, _Mapping]]] = ..., role_pairs: _Optional[_Iterable[_Union[ListOrganizationUsersResponse.RolePair, _Mapping]]] = ...) -> None: ...

class AddOrganizationUsersRequest(_message.Message):
    __slots__ = ("id", "user_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., user_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class AddOrganizationUsersResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveOrganizationUserRequest(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class RemoveOrganizationUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListOrganizationServiceUsersRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListOrganizationServiceUsersResponse(_message.Message):
    __slots__ = ("serviceusers",)
    SERVICEUSERS_FIELD_NUMBER: _ClassVar[int]
    serviceusers: _containers.RepeatedCompositeFieldContainer[_models_pb2.ServiceUser]
    def __init__(self, serviceusers: _Optional[_Iterable[_Union[_models_pb2.ServiceUser, _Mapping]]] = ...) -> None: ...

class ListOrganizationInvitationsRequest(_message.Message):
    __slots__ = ("org_id", "user_id")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    user_id: str
    def __init__(self, org_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class ListOrganizationInvitationsResponse(_message.Message):
    __slots__ = ("invitations",)
    INVITATIONS_FIELD_NUMBER: _ClassVar[int]
    invitations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Invitation]
    def __init__(self, invitations: _Optional[_Iterable[_Union[_models_pb2.Invitation, _Mapping]]] = ...) -> None: ...

class CreateOrganizationInvitationRequest(_message.Message):
    __slots__ = ("org_id", "user_ids", "group_ids", "role_ids")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    USER_IDS_FIELD_NUMBER: _ClassVar[int]
    GROUP_IDS_FIELD_NUMBER: _ClassVar[int]
    ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    user_ids: _containers.RepeatedScalarFieldContainer[str]
    group_ids: _containers.RepeatedScalarFieldContainer[str]
    role_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, org_id: _Optional[str] = ..., user_ids: _Optional[_Iterable[str]] = ..., group_ids: _Optional[_Iterable[str]] = ..., role_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateOrganizationInvitationResponse(_message.Message):
    __slots__ = ("invitations",)
    INVITATIONS_FIELD_NUMBER: _ClassVar[int]
    invitations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Invitation]
    def __init__(self, invitations: _Optional[_Iterable[_Union[_models_pb2.Invitation, _Mapping]]] = ...) -> None: ...

class GetOrganizationInvitationRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class GetOrganizationInvitationResponse(_message.Message):
    __slots__ = ("invitation",)
    INVITATION_FIELD_NUMBER: _ClassVar[int]
    invitation: _models_pb2.Invitation
    def __init__(self, invitation: _Optional[_Union[_models_pb2.Invitation, _Mapping]] = ...) -> None: ...

class AcceptOrganizationInvitationRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class AcceptOrganizationInvitationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteOrganizationInvitationRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class ListOrganizationDomainsRequest(_message.Message):
    __slots__ = ("org_id", "state")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    state: str
    def __init__(self, org_id: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class ListOrganizationDomainsResponse(_message.Message):
    __slots__ = ("domains",)
    DOMAINS_FIELD_NUMBER: _ClassVar[int]
    domains: _containers.RepeatedCompositeFieldContainer[_models_pb2.Domain]
    def __init__(self, domains: _Optional[_Iterable[_Union[_models_pb2.Domain, _Mapping]]] = ...) -> None: ...

class ListOrganizationsByDomainRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ListOrganizationsByDomainResponse(_message.Message):
    __slots__ = ("organizations",)
    ORGANIZATIONS_FIELD_NUMBER: _ClassVar[int]
    organizations: _containers.RepeatedCompositeFieldContainer[_models_pb2.Organization]
    def __init__(self, organizations: _Optional[_Iterable[_Union[_models_pb2.Organization, _Mapping]]] = ...) -> None: ...

class JoinOrganizationRequest(_message.Message):
    __slots__ = ("org_id",)
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    def __init__(self, org_id: _Optional[str] = ...) -> None: ...

class JoinOrganizationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetOrganizationDomainRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class GetOrganizationDomainResponse(_message.Message):
    __slots__ = ("domain",)
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    domain: _models_pb2.Domain
    def __init__(self, domain: _Optional[_Union[_models_pb2.Domain, _Mapping]] = ...) -> None: ...

class CreateOrganizationDomainRequest(_message.Message):
    __slots__ = ("org_id", "domain")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    domain: str
    def __init__(self, org_id: _Optional[str] = ..., domain: _Optional[str] = ...) -> None: ...

class CreateOrganizationDomainResponse(_message.Message):
    __slots__ = ("domain",)
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    domain: _models_pb2.Domain
    def __init__(self, domain: _Optional[_Union[_models_pb2.Domain, _Mapping]] = ...) -> None: ...

class DeleteOrganizationDomainRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DeleteOrganizationDomainResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VerifyOrganizationDomainRequest(_message.Message):
    __slots__ = ("org_id", "id")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    id: str
    def __init__(self, org_id: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class VerifyOrganizationDomainResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: str
    def __init__(self, state: _Optional[str] = ...) -> None: ...

class DeleteOrganizationInvitationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EnableOrganizationRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class EnableOrganizationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DisableOrganizationRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DisableOrganizationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteOrganizationRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteOrganizationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetOrganizationKycRequest(_message.Message):
    __slots__ = ("org_id",)
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    def __init__(self, org_id: _Optional[str] = ...) -> None: ...

class GetOrganizationKycResponse(_message.Message):
    __slots__ = ("organization_kyc",)
    ORGANIZATION_KYC_FIELD_NUMBER: _ClassVar[int]
    organization_kyc: _models_pb2.OrganizationKyc
    def __init__(self, organization_kyc: _Optional[_Union[_models_pb2.OrganizationKyc, _Mapping]] = ...) -> None: ...

class ProjectRequestBody(_message.Message):
    __slots__ = ("name", "title", "metadata", "org_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    title: str
    metadata: _struct_pb2.Struct
    org_id: str
    def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., org_id: _Optional[str] = ...) -> None: ...

class CreateProjectRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: ProjectRequestBody
    def __init__(self, body: _Optional[_Union[ProjectRequestBody, _Mapping]] = ...) -> None: ...

class CreateProjectResponse(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: _models_pb2.Project
    def __init__(self, project: _Optional[_Union[_models_pb2.Project, _Mapping]] = ...) -> None: ...

class ListOrganizationProjectsRequest(_message.Message):
    __slots__ = ("id", "state", "with_member_count")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    WITH_MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: str
    with_member_count: bool
    def __init__(self, id: _Optional[str] = ..., state: _Optional[str] = ..., with_member_count: _Optional[bool] = ...) -> None: ...

class ListOrganizationProjectsResponse(_message.Message):
    __slots__ = ("projects",)
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[_models_pb2.Project]
    def __init__(self, projects: _Optional[_Iterable[_Union[_models_pb2.Project, _Mapping]]] = ...) -> None: ...

class GetProjectRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetProjectResponse(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: _models_pb2.Project
    def __init__(self, project: _Optional[_Union[_models_pb2.Project, _Mapping]] = ...) -> None: ...

class UpdateProjectRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: ProjectRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[ProjectRequestBody, _Mapping]] = ...) -> None: ...

class UpdateProjectResponse(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: _models_pb2.Project
    def __init__(self, project: _Optional[_Union[_models_pb2.Project, _Mapping]] = ...) -> None: ...

class ListProjectAdminsRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListProjectAdminsResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_models_pb2.User]
    def __init__(self, users: _Optional[_Iterable[_Union[_models_pb2.User, _Mapping]]] = ...) -> None: ...

class ListProjectUsersRequest(_message.Message):
    __slots__ = ("id", "permission_filter", "with_roles")
    ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FILTER_FIELD_NUMBER: _ClassVar[int]
    WITH_ROLES_FIELD_NUMBER: _ClassVar[int]
    id: str
    permission_filter: str
    with_roles: bool
    def __init__(self, id: _Optional[str] = ..., permission_filter: _Optional[str] = ..., with_roles: _Optional[bool] = ...) -> None: ...

class ListProjectUsersResponse(_message.Message):
    __slots__ = ("users", "role_pairs")
    class RolePair(_message.Message):
        __slots__ = ("user_id", "roles")
        USER_ID_FIELD_NUMBER: _ClassVar[int]
        ROLES_FIELD_NUMBER: _ClassVar[int]
        user_id: str
        roles: _containers.RepeatedCompositeFieldContainer[_models_pb2.Role]
        def __init__(self, user_id: _Optional[str] = ..., roles: _Optional[_Iterable[_Union[_models_pb2.Role, _Mapping]]] = ...) -> None: ...
    USERS_FIELD_NUMBER: _ClassVar[int]
    ROLE_PAIRS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_models_pb2.User]
    role_pairs: _containers.RepeatedCompositeFieldContainer[ListProjectUsersResponse.RolePair]
    def __init__(self, users: _Optional[_Iterable[_Union[_models_pb2.User, _Mapping]]] = ..., role_pairs: _Optional[_Iterable[_Union[ListProjectUsersResponse.RolePair, _Mapping]]] = ...) -> None: ...

class ListProjectServiceUsersRequest(_message.Message):
    __slots__ = ("id", "with_roles")
    ID_FIELD_NUMBER: _ClassVar[int]
    WITH_ROLES_FIELD_NUMBER: _ClassVar[int]
    id: str
    with_roles: bool
    def __init__(self, id: _Optional[str] = ..., with_roles: _Optional[bool] = ...) -> None: ...

class ListProjectServiceUsersResponse(_message.Message):
    __slots__ = ("serviceusers", "role_pairs")
    class RolePair(_message.Message):
        __slots__ = ("serviceuser_id", "roles")
        SERVICEUSER_ID_FIELD_NUMBER: _ClassVar[int]
        ROLES_FIELD_NUMBER: _ClassVar[int]
        serviceuser_id: str
        roles: _containers.RepeatedCompositeFieldContainer[_models_pb2.Role]
        def __init__(self, serviceuser_id: _Optional[str] = ..., roles: _Optional[_Iterable[_Union[_models_pb2.Role, _Mapping]]] = ...) -> None: ...
    SERVICEUSERS_FIELD_NUMBER: _ClassVar[int]
    ROLE_PAIRS_FIELD_NUMBER: _ClassVar[int]
    serviceusers: _containers.RepeatedCompositeFieldContainer[_models_pb2.ServiceUser]
    role_pairs: _containers.RepeatedCompositeFieldContainer[ListProjectServiceUsersResponse.RolePair]
    def __init__(self, serviceusers: _Optional[_Iterable[_Union[_models_pb2.ServiceUser, _Mapping]]] = ..., role_pairs: _Optional[_Iterable[_Union[ListProjectServiceUsersResponse.RolePair, _Mapping]]] = ...) -> None: ...

class ListProjectGroupsRequest(_message.Message):
    __slots__ = ("id", "with_roles")
    ID_FIELD_NUMBER: _ClassVar[int]
    WITH_ROLES_FIELD_NUMBER: _ClassVar[int]
    id: str
    with_roles: bool
    def __init__(self, id: _Optional[str] = ..., with_roles: _Optional[bool] = ...) -> None: ...

class ListProjectGroupsResponse(_message.Message):
    __slots__ = ("groups", "role_pairs")
    class RolePair(_message.Message):
        __slots__ = ("group_id", "roles")
        GROUP_ID_FIELD_NUMBER: _ClassVar[int]
        ROLES_FIELD_NUMBER: _ClassVar[int]
        group_id: str
        roles: _containers.RepeatedCompositeFieldContainer[_models_pb2.Role]
        def __init__(self, group_id: _Optional[str] = ..., roles: _Optional[_Iterable[_Union[_models_pb2.Role, _Mapping]]] = ...) -> None: ...
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    ROLE_PAIRS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_models_pb2.Group]
    role_pairs: _containers.RepeatedCompositeFieldContainer[ListProjectGroupsResponse.RolePair]
    def __init__(self, groups: _Optional[_Iterable[_Union[_models_pb2.Group, _Mapping]]] = ..., role_pairs: _Optional[_Iterable[_Union[ListProjectGroupsResponse.RolePair, _Mapping]]] = ...) -> None: ...

class EnableProjectRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class EnableProjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DisableProjectRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DisableProjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteProjectRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteProjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PolicyRequestBody(_message.Message):
    __slots__ = ("role_id", "title", "resource", "principal", "metadata")
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    title: str
    resource: str
    principal: str
    metadata: _struct_pb2.Struct
    def __init__(self, role_id: _Optional[str] = ..., title: _Optional[str] = ..., resource: _Optional[str] = ..., principal: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreatePolicyForProjectBody(_message.Message):
    __slots__ = ("role_id", "title", "principal")
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    title: str
    principal: str
    def __init__(self, role_id: _Optional[str] = ..., title: _Optional[str] = ..., principal: _Optional[str] = ...) -> None: ...

class GetPermissionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetPermissionResponse(_message.Message):
    __slots__ = ("permission",)
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    permission: _models_pb2.Permission
    def __init__(self, permission: _Optional[_Union[_models_pb2.Permission, _Mapping]] = ...) -> None: ...

class ListPermissionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPermissionsResponse(_message.Message):
    __slots__ = ("permissions",)
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[_models_pb2.Permission]
    def __init__(self, permissions: _Optional[_Iterable[_Union[_models_pb2.Permission, _Mapping]]] = ...) -> None: ...

class ListNamespacesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNamespacesResponse(_message.Message):
    __slots__ = ("namespaces",)
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    namespaces: _containers.RepeatedCompositeFieldContainer[_models_pb2.Namespace]
    def __init__(self, namespaces: _Optional[_Iterable[_Union[_models_pb2.Namespace, _Mapping]]] = ...) -> None: ...

class GetNamespaceRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetNamespaceResponse(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: _models_pb2.Namespace
    def __init__(self, namespace: _Optional[_Union[_models_pb2.Namespace, _Mapping]] = ...) -> None: ...

class CreatePolicyRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: PolicyRequestBody
    def __init__(self, body: _Optional[_Union[PolicyRequestBody, _Mapping]] = ...) -> None: ...

class CreatePolicyResponse(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: _models_pb2.Policy
    def __init__(self, policy: _Optional[_Union[_models_pb2.Policy, _Mapping]] = ...) -> None: ...

class GetPolicyRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetPolicyResponse(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: _models_pb2.Policy
    def __init__(self, policy: _Optional[_Union[_models_pb2.Policy, _Mapping]] = ...) -> None: ...

class ListPoliciesRequest(_message.Message):
    __slots__ = ("org_id", "project_id", "user_id", "role_id", "group_id")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    project_id: str
    user_id: str
    role_id: str
    group_id: str
    def __init__(self, org_id: _Optional[str] = ..., project_id: _Optional[str] = ..., user_id: _Optional[str] = ..., role_id: _Optional[str] = ..., group_id: _Optional[str] = ...) -> None: ...

class ListPoliciesResponse(_message.Message):
    __slots__ = ("policies",)
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    policies: _containers.RepeatedCompositeFieldContainer[_models_pb2.Policy]
    def __init__(self, policies: _Optional[_Iterable[_Union[_models_pb2.Policy, _Mapping]]] = ...) -> None: ...

class UpdatePolicyRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: PolicyRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[PolicyRequestBody, _Mapping]] = ...) -> None: ...

class UpdatePolicyResponse(_message.Message):
    __slots__ = ("policies",)
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    policies: _containers.RepeatedCompositeFieldContainer[_models_pb2.Policy]
    def __init__(self, policies: _Optional[_Iterable[_Union[_models_pb2.Policy, _Mapping]]] = ...) -> None: ...

class DeletePolicyRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeletePolicyResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreatePolicyForProjectRequest(_message.Message):
    __slots__ = ("project_id", "body")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    body: CreatePolicyForProjectBody
    def __init__(self, project_id: _Optional[str] = ..., body: _Optional[_Union[CreatePolicyForProjectBody, _Mapping]] = ...) -> None: ...

class CreatePolicyForProjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RelationRequestBody(_message.Message):
    __slots__ = ("object", "subject", "relation", "subject_sub_relation")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_SUB_RELATION_FIELD_NUMBER: _ClassVar[int]
    object: str
    subject: str
    relation: str
    subject_sub_relation: str
    def __init__(self, object: _Optional[str] = ..., subject: _Optional[str] = ..., relation: _Optional[str] = ..., subject_sub_relation: _Optional[str] = ...) -> None: ...

class CreateRelationRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: RelationRequestBody
    def __init__(self, body: _Optional[_Union[RelationRequestBody, _Mapping]] = ...) -> None: ...

class CreateRelationResponse(_message.Message):
    __slots__ = ("relation",)
    RELATION_FIELD_NUMBER: _ClassVar[int]
    relation: _models_pb2.Relation
    def __init__(self, relation: _Optional[_Union[_models_pb2.Relation, _Mapping]] = ...) -> None: ...

class GetRelationRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetRelationResponse(_message.Message):
    __slots__ = ("relation",)
    RELATION_FIELD_NUMBER: _ClassVar[int]
    relation: _models_pb2.Relation
    def __init__(self, relation: _Optional[_Union[_models_pb2.Relation, _Mapping]] = ...) -> None: ...

class UpdateRelationRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: RelationRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[RelationRequestBody, _Mapping]] = ...) -> None: ...

class UpdateRelationResponse(_message.Message):
    __slots__ = ("relation",)
    RELATION_FIELD_NUMBER: _ClassVar[int]
    relation: _models_pb2.Relation
    def __init__(self, relation: _Optional[_Union[_models_pb2.Relation, _Mapping]] = ...) -> None: ...

class GroupRequestBody(_message.Message):
    __slots__ = ("name", "title", "metadata")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    title: str
    metadata: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateGroupRequest(_message.Message):
    __slots__ = ("body", "org_id")
    BODY_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    body: GroupRequestBody
    org_id: str
    def __init__(self, body: _Optional[_Union[GroupRequestBody, _Mapping]] = ..., org_id: _Optional[str] = ...) -> None: ...

class GetGroupRequest(_message.Message):
    __slots__ = ("id", "org_id", "with_members")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    WITH_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    with_members: bool
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., with_members: _Optional[bool] = ...) -> None: ...

class CreateGroupResponse(_message.Message):
    __slots__ = ("group",)
    GROUP_FIELD_NUMBER: _ClassVar[int]
    group: _models_pb2.Group
    def __init__(self, group: _Optional[_Union[_models_pb2.Group, _Mapping]] = ...) -> None: ...

class GetGroupResponse(_message.Message):
    __slots__ = ("group",)
    GROUP_FIELD_NUMBER: _ClassVar[int]
    group: _models_pb2.Group
    def __init__(self, group: _Optional[_Union[_models_pb2.Group, _Mapping]] = ...) -> None: ...

class UpdateGroupResponse(_message.Message):
    __slots__ = ("group",)
    GROUP_FIELD_NUMBER: _ClassVar[int]
    group: _models_pb2.Group
    def __init__(self, group: _Optional[_Union[_models_pb2.Group, _Mapping]] = ...) -> None: ...

class UpdateGroupRequest(_message.Message):
    __slots__ = ("id", "body", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: GroupRequestBody
    org_id: str
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[GroupRequestBody, _Mapping]] = ..., org_id: _Optional[str] = ...) -> None: ...

class ListGroupUsersRequest(_message.Message):
    __slots__ = ("id", "org_id", "with_roles")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    WITH_ROLES_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    with_roles: bool
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., with_roles: _Optional[bool] = ...) -> None: ...

class ListGroupUsersResponse(_message.Message):
    __slots__ = ("users", "role_pairs")
    class RolePair(_message.Message):
        __slots__ = ("user_id", "roles")
        USER_ID_FIELD_NUMBER: _ClassVar[int]
        ROLES_FIELD_NUMBER: _ClassVar[int]
        user_id: str
        roles: _containers.RepeatedCompositeFieldContainer[_models_pb2.Role]
        def __init__(self, user_id: _Optional[str] = ..., roles: _Optional[_Iterable[_Union[_models_pb2.Role, _Mapping]]] = ...) -> None: ...
    USERS_FIELD_NUMBER: _ClassVar[int]
    ROLE_PAIRS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_models_pb2.User]
    role_pairs: _containers.RepeatedCompositeFieldContainer[ListGroupUsersResponse.RolePair]
    def __init__(self, users: _Optional[_Iterable[_Union[_models_pb2.User, _Mapping]]] = ..., role_pairs: _Optional[_Iterable[_Union[ListGroupUsersResponse.RolePair, _Mapping]]] = ...) -> None: ...

class EnableGroupRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class EnableGroupResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DisableGroupRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DisableGroupResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteGroupRequest(_message.Message):
    __slots__ = ("id", "org_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ...) -> None: ...

class DeleteGroupResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AddGroupUsersRequest(_message.Message):
    __slots__ = ("id", "org_id", "user_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    USER_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    user_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., user_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class AddGroupUsersResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveGroupUserRequest(_message.Message):
    __slots__ = ("id", "org_id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    org_id: str
    user_id: str
    def __init__(self, id: _Optional[str] = ..., org_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class RemoveGroupUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteRelationRequest(_message.Message):
    __slots__ = ("object", "subject", "relation")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    object: str
    subject: str
    relation: str
    def __init__(self, object: _Optional[str] = ..., subject: _Optional[str] = ..., relation: _Optional[str] = ...) -> None: ...

class DeleteRelationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListProjectResourcesRequest(_message.Message):
    __slots__ = ("project_id", "namespace")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    namespace: str
    def __init__(self, project_id: _Optional[str] = ..., namespace: _Optional[str] = ...) -> None: ...

class ListProjectResourcesResponse(_message.Message):
    __slots__ = ("resources",)
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    resources: _containers.RepeatedCompositeFieldContainer[_models_pb2.Resource]
    def __init__(self, resources: _Optional[_Iterable[_Union[_models_pb2.Resource, _Mapping]]] = ...) -> None: ...

class ResourceRequestBody(_message.Message):
    __slots__ = ("name", "title", "namespace", "principal", "metadata")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    title: str
    namespace: str
    principal: str
    metadata: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., title: _Optional[str] = ..., namespace: _Optional[str] = ..., principal: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateProjectResourceRequest(_message.Message):
    __slots__ = ("body", "project_id", "id")
    BODY_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    body: ResourceRequestBody
    project_id: str
    id: str
    def __init__(self, body: _Optional[_Union[ResourceRequestBody, _Mapping]] = ..., project_id: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class CreateProjectResourceResponse(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: _models_pb2.Resource
    def __init__(self, resource: _Optional[_Union[_models_pb2.Resource, _Mapping]] = ...) -> None: ...

class GetProjectResourceRequest(_message.Message):
    __slots__ = ("id", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class GetProjectResourceResponse(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: _models_pb2.Resource
    def __init__(self, resource: _Optional[_Union[_models_pb2.Resource, _Mapping]] = ...) -> None: ...

class UpdateProjectResourceRequest(_message.Message):
    __slots__ = ("id", "body", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: ResourceRequestBody
    project_id: str
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[ResourceRequestBody, _Mapping]] = ..., project_id: _Optional[str] = ...) -> None: ...

class UpdateProjectResourceResponse(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: _models_pb2.Resource
    def __init__(self, resource: _Optional[_Union[_models_pb2.Resource, _Mapping]] = ...) -> None: ...

class DeleteProjectResourceRequest(_message.Message):
    __slots__ = ("id", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class DeleteProjectResourceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CheckResourcePermissionRequest(_message.Message):
    __slots__ = ("object_id", "object_namespace", "permission", "resource")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    object_namespace: str
    permission: str
    resource: str
    def __init__(self, object_id: _Optional[str] = ..., object_namespace: _Optional[str] = ..., permission: _Optional[str] = ..., resource: _Optional[str] = ...) -> None: ...

class CheckResourcePermissionResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: _Optional[bool] = ...) -> None: ...

class BatchCheckPermissionRequest(_message.Message):
    __slots__ = ("bodies",)
    BODIES_FIELD_NUMBER: _ClassVar[int]
    bodies: _containers.RepeatedCompositeFieldContainer[BatchCheckPermissionBody]
    def __init__(self, bodies: _Optional[_Iterable[_Union[BatchCheckPermissionBody, _Mapping]]] = ...) -> None: ...

class BatchCheckPermissionBody(_message.Message):
    __slots__ = ("permission", "resource")
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    permission: str
    resource: str
    def __init__(self, permission: _Optional[str] = ..., resource: _Optional[str] = ...) -> None: ...

class BatchCheckPermissionResponse(_message.Message):
    __slots__ = ("pairs",)
    PAIRS_FIELD_NUMBER: _ClassVar[int]
    pairs: _containers.RepeatedCompositeFieldContainer[BatchCheckPermissionResponsePair]
    def __init__(self, pairs: _Optional[_Iterable[_Union[BatchCheckPermissionResponsePair, _Mapping]]] = ...) -> None: ...

class BatchCheckPermissionResponsePair(_message.Message):
    __slots__ = ("body", "status")
    BODY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    body: BatchCheckPermissionBody
    status: bool
    def __init__(self, body: _Optional[_Union[BatchCheckPermissionBody, _Mapping]] = ..., status: _Optional[bool] = ...) -> None: ...

class MetaSchemaRequestBody(_message.Message):
    __slots__ = ("name", "schema")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    name: str
    schema: str
    def __init__(self, name: _Optional[str] = ..., schema: _Optional[str] = ...) -> None: ...

class CreateMetaSchemaRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: MetaSchemaRequestBody
    def __init__(self, body: _Optional[_Union[MetaSchemaRequestBody, _Mapping]] = ...) -> None: ...

class CreateMetaSchemaResponse(_message.Message):
    __slots__ = ("metaschema",)
    METASCHEMA_FIELD_NUMBER: _ClassVar[int]
    metaschema: _models_pb2.MetaSchema
    def __init__(self, metaschema: _Optional[_Union[_models_pb2.MetaSchema, _Mapping]] = ...) -> None: ...

class GetMetaSchemaRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetMetaSchemaResponse(_message.Message):
    __slots__ = ("metaschema",)
    METASCHEMA_FIELD_NUMBER: _ClassVar[int]
    metaschema: _models_pb2.MetaSchema
    def __init__(self, metaschema: _Optional[_Union[_models_pb2.MetaSchema, _Mapping]] = ...) -> None: ...

class UpdateMetaSchemaRequest(_message.Message):
    __slots__ = ("id", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    body: MetaSchemaRequestBody
    def __init__(self, id: _Optional[str] = ..., body: _Optional[_Union[MetaSchemaRequestBody, _Mapping]] = ...) -> None: ...

class UpdateMetaSchemaResponse(_message.Message):
    __slots__ = ("metaschema",)
    METASCHEMA_FIELD_NUMBER: _ClassVar[int]
    metaschema: _models_pb2.MetaSchema
    def __init__(self, metaschema: _Optional[_Union[_models_pb2.MetaSchema, _Mapping]] = ...) -> None: ...

class DeleteMetaSchemaRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteMetaSchemaResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListMetaSchemasRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListMetaSchemasResponse(_message.Message):
    __slots__ = ("metaschemas",)
    METASCHEMAS_FIELD_NUMBER: _ClassVar[int]
    metaschemas: _containers.RepeatedCompositeFieldContainer[_models_pb2.MetaSchema]
    def __init__(self, metaschemas: _Optional[_Iterable[_Union[_models_pb2.MetaSchema, _Mapping]]] = ...) -> None: ...

class ListOrganizationAuditLogsRequest(_message.Message):
    __slots__ = ("org_id", "source", "action", "ignore_system", "start_time", "end_time")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    IGNORE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    source: str
    action: str
    ignore_system: bool
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    def __init__(self, org_id: _Optional[str] = ..., source: _Optional[str] = ..., action: _Optional[str] = ..., ignore_system: _Optional[bool] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListOrganizationAuditLogsResponse(_message.Message):
    __slots__ = ("logs",)
    LOGS_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[_models_pb2.AuditLog]
    def __init__(self, logs: _Optional[_Iterable[_Union[_models_pb2.AuditLog, _Mapping]]] = ...) -> None: ...

class CreateOrganizationAuditLogsRequest(_message.Message):
    __slots__ = ("org_id", "logs")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    logs: _containers.RepeatedCompositeFieldContainer[_models_pb2.AuditLog]
    def __init__(self, org_id: _Optional[str] = ..., logs: _Optional[_Iterable[_Union[_models_pb2.AuditLog, _Mapping]]] = ...) -> None: ...

class CreateOrganizationAuditLogsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetOrganizationAuditLogRequest(_message.Message):
    __slots__ = ("org_id", "id")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    id: str
    def __init__(self, org_id: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class GetOrganizationAuditLogResponse(_message.Message):
    __slots__ = ("log",)
    LOG_FIELD_NUMBER: _ClassVar[int]
    log: _models_pb2.AuditLog
    def __init__(self, log: _Optional[_Union[_models_pb2.AuditLog, _Mapping]] = ...) -> None: ...

class DescribePreferencesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DescribePreferencesResponse(_message.Message):
    __slots__ = ("traits",)
    TRAITS_FIELD_NUMBER: _ClassVar[int]
    traits: _containers.RepeatedCompositeFieldContainer[_models_pb2.PreferenceTrait]
    def __init__(self, traits: _Optional[_Iterable[_Union[_models_pb2.PreferenceTrait, _Mapping]]] = ...) -> None: ...

class CreateOrganizationPreferencesRequest(_message.Message):
    __slots__ = ("id", "bodies")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    bodies: _containers.RepeatedCompositeFieldContainer[_models_pb2.PreferenceRequestBody]
    def __init__(self, id: _Optional[str] = ..., bodies: _Optional[_Iterable[_Union[_models_pb2.PreferenceRequestBody, _Mapping]]] = ...) -> None: ...

class CreateOrganizationPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class ListOrganizationPreferencesRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListOrganizationPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class CreateProjectPreferencesRequest(_message.Message):
    __slots__ = ("id", "bodies")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    bodies: _containers.RepeatedCompositeFieldContainer[_models_pb2.PreferenceRequestBody]
    def __init__(self, id: _Optional[str] = ..., bodies: _Optional[_Iterable[_Union[_models_pb2.PreferenceRequestBody, _Mapping]]] = ...) -> None: ...

class CreateProjectPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class ListProjectPreferencesRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListProjectPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class CreateGroupPreferencesRequest(_message.Message):
    __slots__ = ("id", "bodies")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    bodies: _containers.RepeatedCompositeFieldContainer[_models_pb2.PreferenceRequestBody]
    def __init__(self, id: _Optional[str] = ..., bodies: _Optional[_Iterable[_Union[_models_pb2.PreferenceRequestBody, _Mapping]]] = ...) -> None: ...

class CreateGroupPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class ListGroupPreferencesRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListGroupPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class CreateUserPreferencesRequest(_message.Message):
    __slots__ = ("id", "bodies")
    ID_FIELD_NUMBER: _ClassVar[int]
    BODIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    bodies: _containers.RepeatedCompositeFieldContainer[_models_pb2.PreferenceRequestBody]
    def __init__(self, id: _Optional[str] = ..., bodies: _Optional[_Iterable[_Union[_models_pb2.PreferenceRequestBody, _Mapping]]] = ...) -> None: ...

class CreateUserPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class ListUserPreferencesRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListUserPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class CreateCurrentUserPreferencesRequest(_message.Message):
    __slots__ = ("bodies",)
    BODIES_FIELD_NUMBER: _ClassVar[int]
    bodies: _containers.RepeatedCompositeFieldContainer[_models_pb2.PreferenceRequestBody]
    def __init__(self, bodies: _Optional[_Iterable[_Union[_models_pb2.PreferenceRequestBody, _Mapping]]] = ...) -> None: ...

class CreateCurrentUserPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class ListCurrentUserPreferencesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListCurrentUserPreferencesResponse(_message.Message):
    __slots__ = ("preferences",)
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    preferences: _containers.RepeatedCompositeFieldContainer[_models_pb2.Preference]
    def __init__(self, preferences: _Optional[_Iterable[_Union[_models_pb2.Preference, _Mapping]]] = ...) -> None: ...

class BillingWebhookCallbackRequest(_message.Message):
    __slots__ = ("provider", "body")
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    provider: str
    body: bytes
    def __init__(self, provider: _Optional[str] = ..., body: _Optional[bytes] = ...) -> None: ...

class BillingWebhookCallbackResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateProspectPublicRequest(_message.Message):
    __slots__ = ("name", "email", "phone", "activity", "source", "metadata")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    email: str
    phone: str
    activity: str
    source: str
    metadata: _struct_pb2.Struct
    def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., activity: _Optional[str] = ..., source: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateProspectPublicResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSessionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSessionsResponse(_message.Message):
    __slots__ = ("sessions",)
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedCompositeFieldContainer[_models_pb2.Session]
    def __init__(self, sessions: _Optional[_Iterable[_Union[_models_pb2.Session, _Mapping]]] = ...) -> None: ...

class RevokeSessionRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class RevokeSessionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PingUserSessionRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PingUserSessionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateAuditRecordRequest(_message.Message):
    __slots__ = ("actor", "event", "resource", "target", "occurred_at", "org_id", "request_id", "metadata", "idempotency_key")
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_AT_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    actor: _models_pb2.AuditRecordActor
    event: str
    resource: _models_pb2.AuditRecordResource
    target: _models_pb2.AuditRecordTarget
    occurred_at: _timestamp_pb2.Timestamp
    org_id: str
    request_id: str
    metadata: _struct_pb2.Struct
    idempotency_key: str
    def __init__(self, actor: _Optional[_Union[_models_pb2.AuditRecordActor, _Mapping]] = ..., event: _Optional[str] = ..., resource: _Optional[_Union[_models_pb2.AuditRecordResource, _Mapping]] = ..., target: _Optional[_Union[_models_pb2.AuditRecordTarget, _Mapping]] = ..., occurred_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., org_id: _Optional[str] = ..., request_id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., idempotency_key: _Optional[str] = ...) -> None: ...

class CreateAuditRecordResponse(_message.Message):
    __slots__ = ("audit_record",)
    AUDIT_RECORD_FIELD_NUMBER: _ClassVar[int]
    audit_record: _models_pb2.AuditRecord
    def __init__(self, audit_record: _Optional[_Union[_models_pb2.AuditRecord, _Mapping]] = ...) -> None: ...
