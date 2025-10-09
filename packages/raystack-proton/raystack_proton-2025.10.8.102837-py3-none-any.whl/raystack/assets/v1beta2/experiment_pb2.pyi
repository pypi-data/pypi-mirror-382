import datetime

from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Experiment(_message.Message):
    __slots__ = ("entity", "traffic_percent", "variants", "attributes", "create_time", "update_time")
    class Variant(_message.Message):
        __slots__ = ("name", "traffic_percent", "is_control", "attributes", "is_promoted")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TRAFFIC_PERCENT_FIELD_NUMBER: _ClassVar[int]
        IS_CONTROL_FIELD_NUMBER: _ClassVar[int]
        ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
        IS_PROMOTED_FIELD_NUMBER: _ClassVar[int]
        name: str
        traffic_percent: float
        is_control: bool
        attributes: _struct_pb2.Struct
        is_promoted: bool
        def __init__(self, name: _Optional[str] = ..., traffic_percent: _Optional[float] = ..., is_control: _Optional[bool] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., is_promoted: _Optional[bool] = ...) -> None: ...
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    TRAFFIC_PERCENT_FIELD_NUMBER: _ClassVar[int]
    VARIANTS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    entity: str
    traffic_percent: float
    variants: _containers.RepeatedCompositeFieldContainer[Experiment.Variant]
    attributes: _struct_pb2.Struct
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    def __init__(self, entity: _Optional[str] = ..., traffic_percent: _Optional[float] = ..., variants: _Optional[_Iterable[_Union[Experiment.Variant, _Mapping]]] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
