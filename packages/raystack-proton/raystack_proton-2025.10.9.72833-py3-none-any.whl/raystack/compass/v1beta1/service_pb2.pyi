import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAllDiscussionsRequest(_message.Message):
    __slots__ = ("type", "state", "owner", "assignee", "asset", "labels", "sort", "direction", "size", "offset")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEE_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    type: str
    state: str
    owner: str
    assignee: str
    asset: str
    labels: str
    sort: str
    direction: str
    size: int
    offset: int
    def __init__(self, type: _Optional[str] = ..., state: _Optional[str] = ..., owner: _Optional[str] = ..., assignee: _Optional[str] = ..., asset: _Optional[str] = ..., labels: _Optional[str] = ..., sort: _Optional[str] = ..., direction: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetAllDiscussionsResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Discussion]
    def __init__(self, data: _Optional[_Iterable[_Union[Discussion, _Mapping]]] = ...) -> None: ...

class CreateDiscussionRequest(_message.Message):
    __slots__ = ("title", "body", "type", "state", "labels", "assets", "assignees")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEES_FIELD_NUMBER: _ClassVar[int]
    title: str
    body: str
    type: str
    state: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    assets: _containers.RepeatedScalarFieldContainer[str]
    assignees: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, title: _Optional[str] = ..., body: _Optional[str] = ..., type: _Optional[str] = ..., state: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ..., assets: _Optional[_Iterable[str]] = ..., assignees: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateDiscussionResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetDiscussionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetDiscussionResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Discussion
    def __init__(self, data: _Optional[_Union[Discussion, _Mapping]] = ...) -> None: ...

class PatchDiscussionRequest(_message.Message):
    __slots__ = ("id", "title", "body", "type", "state", "labels", "assets", "assignees")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEES_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    body: str
    type: str
    state: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    assets: _containers.RepeatedScalarFieldContainer[str]
    assignees: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., type: _Optional[str] = ..., state: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ..., assets: _Optional[_Iterable[str]] = ..., assignees: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateCommentRequest(_message.Message):
    __slots__ = ("discussion_id", "body")
    DISCUSSION_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    discussion_id: str
    body: str
    def __init__(self, discussion_id: _Optional[str] = ..., body: _Optional[str] = ...) -> None: ...

class PatchDiscussionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateCommentResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetAllCommentsRequest(_message.Message):
    __slots__ = ("discussion_id", "sort", "direction", "size", "offset")
    DISCUSSION_ID_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    discussion_id: str
    sort: str
    direction: str
    size: int
    offset: int
    def __init__(self, discussion_id: _Optional[str] = ..., sort: _Optional[str] = ..., direction: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetAllCommentsResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Comment]
    def __init__(self, data: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ...) -> None: ...

class GetCommentRequest(_message.Message):
    __slots__ = ("discussion_id", "id")
    DISCUSSION_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    discussion_id: str
    id: str
    def __init__(self, discussion_id: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class GetCommentResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Comment
    def __init__(self, data: _Optional[_Union[Comment, _Mapping]] = ...) -> None: ...

class UpdateCommentRequest(_message.Message):
    __slots__ = ("discussion_id", "id", "body")
    DISCUSSION_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    discussion_id: str
    id: str
    body: str
    def __init__(self, discussion_id: _Optional[str] = ..., id: _Optional[str] = ..., body: _Optional[str] = ...) -> None: ...

class UpdateCommentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteCommentRequest(_message.Message):
    __slots__ = ("discussion_id", "id")
    DISCUSSION_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    discussion_id: str
    id: str
    def __init__(self, discussion_id: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class DeleteCommentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SearchAssetsRequest(_message.Message):
    __slots__ = ("text", "rankby", "size", "filter", "query", "include_fields", "offset")
    class FilterEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class QueryEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TEXT_FIELD_NUMBER: _ClassVar[int]
    RANKBY_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_FIELDS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    text: str
    rankby: str
    size: int
    filter: _containers.ScalarMap[str, str]
    query: _containers.ScalarMap[str, str]
    include_fields: _containers.RepeatedScalarFieldContainer[str]
    offset: int
    def __init__(self, text: _Optional[str] = ..., rankby: _Optional[str] = ..., size: _Optional[int] = ..., filter: _Optional[_Mapping[str, str]] = ..., query: _Optional[_Mapping[str, str]] = ..., include_fields: _Optional[_Iterable[str]] = ..., offset: _Optional[int] = ...) -> None: ...

class SearchAssetsResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Asset]
    def __init__(self, data: _Optional[_Iterable[_Union[Asset, _Mapping]]] = ...) -> None: ...

class SuggestAssetsRequest(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class SuggestAssetsResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, data: _Optional[_Iterable[str]] = ...) -> None: ...

class GetGraphRequest(_message.Message):
    __slots__ = ("urn", "level", "direction")
    URN_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    urn: str
    level: int
    direction: str
    def __init__(self, urn: _Optional[str] = ..., level: _Optional[int] = ..., direction: _Optional[str] = ...) -> None: ...

class GetGraphResponse(_message.Message):
    __slots__ = ("data", "node_attrs")
    class ProbesInfo(_message.Message):
        __slots__ = ("latest",)
        LATEST_FIELD_NUMBER: _ClassVar[int]
        latest: Probe
        def __init__(self, latest: _Optional[_Union[Probe, _Mapping]] = ...) -> None: ...
    class NodeAttributes(_message.Message):
        __slots__ = ("probes",)
        PROBES_FIELD_NUMBER: _ClassVar[int]
        probes: GetGraphResponse.ProbesInfo
        def __init__(self, probes: _Optional[_Union[GetGraphResponse.ProbesInfo, _Mapping]] = ...) -> None: ...
    class NodeAttrsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: GetGraphResponse.NodeAttributes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[GetGraphResponse.NodeAttributes, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    NODE_ATTRS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[LineageEdge]
    node_attrs: _containers.MessageMap[str, GetGraphResponse.NodeAttributes]
    def __init__(self, data: _Optional[_Iterable[_Union[LineageEdge, _Mapping]]] = ..., node_attrs: _Optional[_Mapping[str, GetGraphResponse.NodeAttributes]] = ...) -> None: ...

class GetAllTypesRequest(_message.Message):
    __slots__ = ("q", "q_fields", "types", "services", "data")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    Q_FIELD_NUMBER: _ClassVar[int]
    Q_FIELDS_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    q: str
    q_fields: str
    types: str
    services: str
    data: _containers.ScalarMap[str, str]
    def __init__(self, q: _Optional[str] = ..., q_fields: _Optional[str] = ..., types: _Optional[str] = ..., services: _Optional[str] = ..., data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetAllTypesResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Type]
    def __init__(self, data: _Optional[_Iterable[_Union[Type, _Mapping]]] = ...) -> None: ...

class GetAllAssetsRequest(_message.Message):
    __slots__ = ("q", "q_fields", "types", "services", "sort", "direction", "data", "size", "offset", "with_total")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    Q_FIELD_NUMBER: _ClassVar[int]
    Q_FIELDS_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    WITH_TOTAL_FIELD_NUMBER: _ClassVar[int]
    q: str
    q_fields: str
    types: str
    services: str
    sort: str
    direction: str
    data: _containers.ScalarMap[str, str]
    size: int
    offset: int
    with_total: bool
    def __init__(self, q: _Optional[str] = ..., q_fields: _Optional[str] = ..., types: _Optional[str] = ..., services: _Optional[str] = ..., sort: _Optional[str] = ..., direction: _Optional[str] = ..., data: _Optional[_Mapping[str, str]] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ..., with_total: _Optional[bool] = ...) -> None: ...

class GetAllAssetsResponse(_message.Message):
    __slots__ = ("data", "total")
    DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Asset]
    total: int
    def __init__(self, data: _Optional[_Iterable[_Union[Asset, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class GetAssetByIDRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetAssetByIDResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Asset
    def __init__(self, data: _Optional[_Union[Asset, _Mapping]] = ...) -> None: ...

class UpsertAssetRequest(_message.Message):
    __slots__ = ("asset", "upstreams", "downstreams")
    class Asset(_message.Message):
        __slots__ = ("urn", "type", "name", "service", "description", "data", "labels", "owners", "url")
        class LabelsEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        URN_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        SERVICE_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DATA_FIELD_NUMBER: _ClassVar[int]
        LABELS_FIELD_NUMBER: _ClassVar[int]
        OWNERS_FIELD_NUMBER: _ClassVar[int]
        URL_FIELD_NUMBER: _ClassVar[int]
        urn: str
        type: str
        name: str
        service: str
        description: str
        data: _struct_pb2.Struct
        labels: _containers.ScalarMap[str, str]
        owners: _containers.RepeatedCompositeFieldContainer[User]
        url: str
        def __init__(self, urn: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., service: _Optional[str] = ..., description: _Optional[str] = ..., data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., owners: _Optional[_Iterable[_Union[User, _Mapping]]] = ..., url: _Optional[str] = ...) -> None: ...
    ASSET_FIELD_NUMBER: _ClassVar[int]
    UPSTREAMS_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAMS_FIELD_NUMBER: _ClassVar[int]
    asset: UpsertAssetRequest.Asset
    upstreams: _containers.RepeatedCompositeFieldContainer[LineageNode]
    downstreams: _containers.RepeatedCompositeFieldContainer[LineageNode]
    def __init__(self, asset: _Optional[_Union[UpsertAssetRequest.Asset, _Mapping]] = ..., upstreams: _Optional[_Iterable[_Union[LineageNode, _Mapping]]] = ..., downstreams: _Optional[_Iterable[_Union[LineageNode, _Mapping]]] = ...) -> None: ...

class UpsertAssetResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class UpsertPatchAssetRequest(_message.Message):
    __slots__ = ("asset", "upstreams", "downstreams", "overwrite_lineage")
    class Asset(_message.Message):
        __slots__ = ("urn", "type", "name", "service", "description", "data", "labels", "owners", "url")
        class LabelsEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        URN_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        SERVICE_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        DATA_FIELD_NUMBER: _ClassVar[int]
        LABELS_FIELD_NUMBER: _ClassVar[int]
        OWNERS_FIELD_NUMBER: _ClassVar[int]
        URL_FIELD_NUMBER: _ClassVar[int]
        urn: str
        type: str
        name: _wrappers_pb2.StringValue
        service: str
        description: _wrappers_pb2.StringValue
        data: _struct_pb2.Struct
        labels: _containers.ScalarMap[str, str]
        owners: _containers.RepeatedCompositeFieldContainer[User]
        url: str
        def __init__(self, urn: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., service: _Optional[str] = ..., description: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., owners: _Optional[_Iterable[_Union[User, _Mapping]]] = ..., url: _Optional[str] = ...) -> None: ...
    ASSET_FIELD_NUMBER: _ClassVar[int]
    UPSTREAMS_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAMS_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_LINEAGE_FIELD_NUMBER: _ClassVar[int]
    asset: UpsertPatchAssetRequest.Asset
    upstreams: _containers.RepeatedCompositeFieldContainer[LineageNode]
    downstreams: _containers.RepeatedCompositeFieldContainer[LineageNode]
    overwrite_lineage: bool
    def __init__(self, asset: _Optional[_Union[UpsertPatchAssetRequest.Asset, _Mapping]] = ..., upstreams: _Optional[_Iterable[_Union[LineageNode, _Mapping]]] = ..., downstreams: _Optional[_Iterable[_Union[LineageNode, _Mapping]]] = ..., overwrite_lineage: _Optional[bool] = ...) -> None: ...

class UpsertPatchAssetResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteAssetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteAssetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAssetStargazersRequest(_message.Message):
    __slots__ = ("id", "size", "offset")
    ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    id: str
    size: int
    offset: int
    def __init__(self, id: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetAssetStargazersResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, data: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class GetAssetVersionHistoryRequest(_message.Message):
    __slots__ = ("id", "size", "offset")
    ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    id: str
    size: int
    offset: int
    def __init__(self, id: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetAssetVersionHistoryResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Asset]
    def __init__(self, data: _Optional[_Iterable[_Union[Asset, _Mapping]]] = ...) -> None: ...

class GetAssetByVersionRequest(_message.Message):
    __slots__ = ("id", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: str
    version: str
    def __init__(self, id: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class GetAssetByVersionResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Asset
    def __init__(self, data: _Optional[_Union[Asset, _Mapping]] = ...) -> None: ...

class CreateAssetProbeRequest(_message.Message):
    __slots__ = ("asset_urn", "probe")
    class Probe(_message.Message):
        __slots__ = ("status", "status_reason", "metadata", "timestamp")
        STATUS_FIELD_NUMBER: _ClassVar[int]
        STATUS_REASON_FIELD_NUMBER: _ClassVar[int]
        METADATA_FIELD_NUMBER: _ClassVar[int]
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        status: str
        status_reason: str
        metadata: _struct_pb2.Struct
        timestamp: _timestamp_pb2.Timestamp
        def __init__(self, status: _Optional[str] = ..., status_reason: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    ASSET_URN_FIELD_NUMBER: _ClassVar[int]
    PROBE_FIELD_NUMBER: _ClassVar[int]
    asset_urn: str
    probe: CreateAssetProbeRequest.Probe
    def __init__(self, asset_urn: _Optional[str] = ..., probe: _Optional[_Union[CreateAssetProbeRequest.Probe, _Mapping]] = ...) -> None: ...

class CreateAssetProbeResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetUserStarredAssetsRequest(_message.Message):
    __slots__ = ("user_id", "size", "offset")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    size: int
    offset: int
    def __init__(self, user_id: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetUserStarredAssetsResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Asset]
    def __init__(self, data: _Optional[_Iterable[_Union[Asset, _Mapping]]] = ...) -> None: ...

class GetMyStarredAssetsRequest(_message.Message):
    __slots__ = ("size", "offset")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    size: int
    offset: int
    def __init__(self, size: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetMyStarredAssetsResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Asset]
    def __init__(self, data: _Optional[_Iterable[_Union[Asset, _Mapping]]] = ...) -> None: ...

class GetMyStarredAssetRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class GetMyStarredAssetResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Asset
    def __init__(self, data: _Optional[_Union[Asset, _Mapping]] = ...) -> None: ...

class StarAssetRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class StarAssetResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class UnstarAssetRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class UnstarAssetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetMyDiscussionsRequest(_message.Message):
    __slots__ = ("filter", "type", "state", "asset", "labels", "sort", "direction", "size", "offset")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    filter: str
    type: str
    state: str
    asset: str
    labels: str
    sort: str
    direction: str
    size: int
    offset: int
    def __init__(self, filter: _Optional[str] = ..., type: _Optional[str] = ..., state: _Optional[str] = ..., asset: _Optional[str] = ..., labels: _Optional[str] = ..., sort: _Optional[str] = ..., direction: _Optional[str] = ..., size: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetMyDiscussionsResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Discussion]
    def __init__(self, data: _Optional[_Iterable[_Union[Discussion, _Mapping]]] = ...) -> None: ...

class CreateTagAssetRequest(_message.Message):
    __slots__ = ("asset_id", "template_urn", "tag_values", "template_display_name", "template_description")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_URN_FIELD_NUMBER: _ClassVar[int]
    TAG_VALUES_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    template_urn: str
    tag_values: _containers.RepeatedCompositeFieldContainer[TagValue]
    template_display_name: str
    template_description: str
    def __init__(self, asset_id: _Optional[str] = ..., template_urn: _Optional[str] = ..., tag_values: _Optional[_Iterable[_Union[TagValue, _Mapping]]] = ..., template_display_name: _Optional[str] = ..., template_description: _Optional[str] = ...) -> None: ...

class CreateTagAssetResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Tag
    def __init__(self, data: _Optional[_Union[Tag, _Mapping]] = ...) -> None: ...

class GetTagByAssetAndTemplateRequest(_message.Message):
    __slots__ = ("asset_id", "template_urn")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_URN_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    template_urn: str
    def __init__(self, asset_id: _Optional[str] = ..., template_urn: _Optional[str] = ...) -> None: ...

class GetTagByAssetAndTemplateResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Tag
    def __init__(self, data: _Optional[_Union[Tag, _Mapping]] = ...) -> None: ...

class UpdateTagAssetRequest(_message.Message):
    __slots__ = ("asset_id", "template_urn", "tag_values", "template_display_name", "template_description")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_URN_FIELD_NUMBER: _ClassVar[int]
    TAG_VALUES_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    template_urn: str
    tag_values: _containers.RepeatedCompositeFieldContainer[TagValue]
    template_display_name: str
    template_description: str
    def __init__(self, asset_id: _Optional[str] = ..., template_urn: _Optional[str] = ..., tag_values: _Optional[_Iterable[_Union[TagValue, _Mapping]]] = ..., template_display_name: _Optional[str] = ..., template_description: _Optional[str] = ...) -> None: ...

class UpdateTagAssetResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Tag
    def __init__(self, data: _Optional[_Union[Tag, _Mapping]] = ...) -> None: ...

class DeleteTagAssetRequest(_message.Message):
    __slots__ = ("asset_id", "template_urn")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_URN_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    template_urn: str
    def __init__(self, asset_id: _Optional[str] = ..., template_urn: _Optional[str] = ...) -> None: ...

class DeleteTagAssetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllTagsByAssetRequest(_message.Message):
    __slots__ = ("asset_id",)
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    def __init__(self, asset_id: _Optional[str] = ...) -> None: ...

class GetAllTagsByAssetResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Tag]
    def __init__(self, data: _Optional[_Iterable[_Union[Tag, _Mapping]]] = ...) -> None: ...

class GetAllTagTemplatesRequest(_message.Message):
    __slots__ = ("urn",)
    URN_FIELD_NUMBER: _ClassVar[int]
    urn: str
    def __init__(self, urn: _Optional[str] = ...) -> None: ...

class GetAllTagTemplatesResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[TagTemplate]
    def __init__(self, data: _Optional[_Iterable[_Union[TagTemplate, _Mapping]]] = ...) -> None: ...

class CreateTagTemplateRequest(_message.Message):
    __slots__ = ("urn", "display_name", "description", "fields")
    URN_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    urn: str
    display_name: str
    description: str
    fields: _containers.RepeatedCompositeFieldContainer[TagTemplateField]
    def __init__(self, urn: _Optional[str] = ..., display_name: _Optional[str] = ..., description: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[TagTemplateField, _Mapping]]] = ...) -> None: ...

class CreateTagTemplateResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: TagTemplate
    def __init__(self, data: _Optional[_Union[TagTemplate, _Mapping]] = ...) -> None: ...

class GetTagTemplateRequest(_message.Message):
    __slots__ = ("template_urn",)
    TEMPLATE_URN_FIELD_NUMBER: _ClassVar[int]
    template_urn: str
    def __init__(self, template_urn: _Optional[str] = ...) -> None: ...

class GetTagTemplateResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: TagTemplate
    def __init__(self, data: _Optional[_Union[TagTemplate, _Mapping]] = ...) -> None: ...

class UpdateTagTemplateRequest(_message.Message):
    __slots__ = ("template_urn", "display_name", "description", "fields")
    TEMPLATE_URN_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    template_urn: str
    display_name: str
    description: str
    fields: _containers.RepeatedCompositeFieldContainer[TagTemplateField]
    def __init__(self, template_urn: _Optional[str] = ..., display_name: _Optional[str] = ..., description: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[TagTemplateField, _Mapping]]] = ...) -> None: ...

class UpdateTagTemplateResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: TagTemplate
    def __init__(self, data: _Optional[_Union[TagTemplate, _Mapping]] = ...) -> None: ...

class DeleteTagTemplateRequest(_message.Message):
    __slots__ = ("template_urn",)
    TEMPLATE_URN_FIELD_NUMBER: _ClassVar[int]
    template_urn: str
    def __init__(self, template_urn: _Optional[str] = ...) -> None: ...

class DeleteTagTemplateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateNamespaceRequest(_message.Message):
    __slots__ = ("id", "name", "state", "metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    state: str
    metadata: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., state: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CreateNamespaceResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetNamespaceRequest(_message.Message):
    __slots__ = ("urn",)
    URN_FIELD_NUMBER: _ClassVar[int]
    urn: str
    def __init__(self, urn: _Optional[str] = ...) -> None: ...

class GetNamespaceResponse(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: Namespace
    def __init__(self, namespace: _Optional[_Union[Namespace, _Mapping]] = ...) -> None: ...

class UpdateNamespaceRequest(_message.Message):
    __slots__ = ("urn", "state", "metadata")
    URN_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    urn: str
    state: str
    metadata: _struct_pb2.Struct
    def __init__(self, urn: _Optional[str] = ..., state: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdateNamespaceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNamespacesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNamespacesResponse(_message.Message):
    __slots__ = ("namespaces",)
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    namespaces: _containers.RepeatedCompositeFieldContainer[Namespace]
    def __init__(self, namespaces: _Optional[_Iterable[_Union[Namespace, _Mapping]]] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("id", "uuid", "email", "provider", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    uuid: str
    email: str
    provider: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., uuid: _Optional[str] = ..., email: _Optional[str] = ..., provider: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Change(_message.Message):
    __slots__ = ("type", "path", "to")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    type: str
    path: _containers.RepeatedScalarFieldContainer[str]
    to: _struct_pb2.Value
    def __init__(self, type: _Optional[str] = ..., path: _Optional[_Iterable[str]] = ..., to: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., **kwargs) -> None: ...

class Asset(_message.Message):
    __slots__ = ("id", "urn", "type", "service", "name", "description", "data", "labels", "owners", "version", "updated_by", "changelog", "created_at", "updated_at", "url", "probes")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    OWNERS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    CHANGELOG_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    PROBES_FIELD_NUMBER: _ClassVar[int]
    id: str
    urn: str
    type: str
    service: str
    name: str
    description: str
    data: _struct_pb2.Struct
    labels: _containers.ScalarMap[str, str]
    owners: _containers.RepeatedCompositeFieldContainer[User]
    version: str
    updated_by: User
    changelog: _containers.RepeatedCompositeFieldContainer[Change]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    url: str
    probes: _containers.RepeatedCompositeFieldContainer[Probe]
    def __init__(self, id: _Optional[str] = ..., urn: _Optional[str] = ..., type: _Optional[str] = ..., service: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., owners: _Optional[_Iterable[_Union[User, _Mapping]]] = ..., version: _Optional[str] = ..., updated_by: _Optional[_Union[User, _Mapping]] = ..., changelog: _Optional[_Iterable[_Union[Change, _Mapping]]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., url: _Optional[str] = ..., probes: _Optional[_Iterable[_Union[Probe, _Mapping]]] = ...) -> None: ...

class Probe(_message.Message):
    __slots__ = ("id", "asset_urn", "status", "status_reason", "metadata", "timestamp", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSET_URN_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_REASON_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    asset_urn: str
    status: str
    status_reason: str
    metadata: _struct_pb2.Struct
    timestamp: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., asset_urn: _Optional[str] = ..., status: _Optional[str] = ..., status_reason: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Discussion(_message.Message):
    __slots__ = ("id", "title", "body", "type", "state", "labels", "assets", "assignees", "owner", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEES_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    body: str
    type: str
    state: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    assets: _containers.RepeatedScalarFieldContainer[str]
    assignees: _containers.RepeatedScalarFieldContainer[str]
    owner: User
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., type: _Optional[str] = ..., state: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ..., assets: _Optional[_Iterable[str]] = ..., assignees: _Optional[_Iterable[str]] = ..., owner: _Optional[_Union[User, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Comment(_message.Message):
    __slots__ = ("id", "discussion_id", "body", "owner", "updated_by", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    DISCUSSION_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    discussion_id: str
    body: str
    owner: User
    updated_by: User
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., discussion_id: _Optional[str] = ..., body: _Optional[str] = ..., owner: _Optional[_Union[User, _Mapping]] = ..., updated_by: _Optional[_Union[User, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class LineageEdge(_message.Message):
    __slots__ = ("source", "target", "prop")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    PROP_FIELD_NUMBER: _ClassVar[int]
    source: str
    target: str
    prop: _struct_pb2.Struct
    def __init__(self, source: _Optional[str] = ..., target: _Optional[str] = ..., prop: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class LineageNode(_message.Message):
    __slots__ = ("urn", "type", "service")
    URN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    urn: str
    type: str
    service: str
    def __init__(self, urn: _Optional[str] = ..., type: _Optional[str] = ..., service: _Optional[str] = ...) -> None: ...

class Tag(_message.Message):
    __slots__ = ("asset_id", "template_urn", "tag_values", "template_display_name", "template_description")
    ASSET_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_URN_FIELD_NUMBER: _ClassVar[int]
    TAG_VALUES_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    asset_id: str
    template_urn: str
    tag_values: _containers.RepeatedCompositeFieldContainer[TagValue]
    template_display_name: str
    template_description: str
    def __init__(self, asset_id: _Optional[str] = ..., template_urn: _Optional[str] = ..., tag_values: _Optional[_Iterable[_Union[TagValue, _Mapping]]] = ..., template_display_name: _Optional[str] = ..., template_description: _Optional[str] = ...) -> None: ...

class TagValue(_message.Message):
    __slots__ = ("field_id", "field_value", "field_urn", "field_display_name", "field_description", "field_data_type", "field_options", "field_required", "created_at", "updated_at")
    FIELD_ID_FIELD_NUMBER: _ClassVar[int]
    FIELD_VALUE_FIELD_NUMBER: _ClassVar[int]
    FIELD_URN_FIELD_NUMBER: _ClassVar[int]
    FIELD_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    FIELD_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FIELD_DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIELD_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    FIELD_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    field_id: int
    field_value: _struct_pb2.Value
    field_urn: str
    field_display_name: str
    field_description: str
    field_data_type: str
    field_options: _containers.RepeatedScalarFieldContainer[str]
    field_required: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, field_id: _Optional[int] = ..., field_value: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., field_urn: _Optional[str] = ..., field_display_name: _Optional[str] = ..., field_description: _Optional[str] = ..., field_data_type: _Optional[str] = ..., field_options: _Optional[_Iterable[str]] = ..., field_required: _Optional[bool] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TagTemplate(_message.Message):
    __slots__ = ("urn", "display_name", "description", "fields", "created_at", "updated_at")
    URN_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    urn: str
    display_name: str
    description: str
    fields: _containers.RepeatedCompositeFieldContainer[TagTemplateField]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, urn: _Optional[str] = ..., display_name: _Optional[str] = ..., description: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[TagTemplateField, _Mapping]]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TagTemplateField(_message.Message):
    __slots__ = ("id", "urn", "display_name", "description", "data_type", "options", "required", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    urn: str
    display_name: str
    description: str
    data_type: str
    options: _containers.RepeatedScalarFieldContainer[str]
    required: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., urn: _Optional[str] = ..., display_name: _Optional[str] = ..., description: _Optional[str] = ..., data_type: _Optional[str] = ..., options: _Optional[_Iterable[str]] = ..., required: _Optional[bool] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Type(_message.Message):
    __slots__ = ("name", "count")
    NAME_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    name: str
    count: int
    def __init__(self, name: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class Namespace(_message.Message):
    __slots__ = ("id", "name", "state", "metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    state: str
    metadata: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., state: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
