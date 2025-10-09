from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Preview(_message.Message):
    __slots__ = ("fields", "rows")
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.RepeatedScalarFieldContainer[str]
    rows: _struct_pb2.ListValue
    def __init__(self, fields: _Optional[_Iterable[str]] = ..., rows: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ...) -> None: ...
