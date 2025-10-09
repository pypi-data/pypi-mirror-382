import datetime

from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Topic(_message.Message):
    __slots__ = ("profile", "schema", "attributes", "create_time", "update_time")
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    profile: TopicProfile
    schema: TopicSchema
    attributes: _struct_pb2.Struct
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    def __init__(self, profile: _Optional[_Union[TopicProfile, _Mapping]] = ..., schema: _Optional[_Union[TopicSchema, _Mapping]] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TopicProfile(_message.Message):
    __slots__ = ("throughput", "number_of_partitions")
    THROUGHPUT_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    throughput: str
    number_of_partitions: int
    def __init__(self, throughput: _Optional[str] = ..., number_of_partitions: _Optional[int] = ...) -> None: ...

class TopicSchema(_message.Message):
    __slots__ = ("schema_url", "format")
    SCHEMA_URL_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    schema_url: str
    format: str
    def __init__(self, schema_url: _Optional[str] = ..., format: _Optional[str] = ...) -> None: ...
