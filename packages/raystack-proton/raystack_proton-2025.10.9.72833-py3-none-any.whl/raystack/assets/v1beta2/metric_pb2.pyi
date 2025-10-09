import datetime

from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Metric(_message.Message):
    __slots__ = ("namespace", "field_name", "measure_type", "query", "attributes", "create_time", "update_time")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    FIELD_NAME_FIELD_NUMBER: _ClassVar[int]
    MEASURE_TYPE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    field_name: str
    measure_type: str
    query: str
    attributes: _struct_pb2.Struct
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    def __init__(self, namespace: _Optional[str] = ..., field_name: _Optional[str] = ..., measure_type: _Optional[str] = ..., query: _Optional[str] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
