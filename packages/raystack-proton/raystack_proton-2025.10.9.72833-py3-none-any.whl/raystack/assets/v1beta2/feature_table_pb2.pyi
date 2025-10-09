import datetime

from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Feature(_message.Message):
    __slots__ = ("name", "data_type", "algorithm", "entity_name")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    ENTITY_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    data_type: str
    algorithm: str
    entity_name: str
    def __init__(self, name: _Optional[str] = ..., data_type: _Optional[str] = ..., algorithm: _Optional[str] = ..., entity_name: _Optional[str] = ...) -> None: ...

class FeatureTable(_message.Message):
    __slots__ = ("namespace", "entities", "features", "attributes", "create_time", "update_time")
    class Entity(_message.Message):
        __slots__ = ("name", "join_keys", "labels", "description", "type")
        class LabelsEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        NAME_FIELD_NUMBER: _ClassVar[int]
        JOIN_KEYS_FIELD_NUMBER: _ClassVar[int]
        LABELS_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        name: str
        join_keys: _containers.RepeatedScalarFieldContainer[str]
        labels: _containers.ScalarMap[str, str]
        description: str
        type: str
        def __init__(self, name: _Optional[str] = ..., join_keys: _Optional[_Iterable[str]] = ..., labels: _Optional[_Mapping[str, str]] = ..., description: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    entities: _containers.RepeatedCompositeFieldContainer[FeatureTable.Entity]
    features: _containers.RepeatedCompositeFieldContainer[Feature]
    attributes: _struct_pb2.Struct
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    def __init__(self, namespace: _Optional[str] = ..., entities: _Optional[_Iterable[_Union[FeatureTable.Entity, _Mapping]]] = ..., features: _Optional[_Iterable[_Union[Feature, _Mapping]]] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
