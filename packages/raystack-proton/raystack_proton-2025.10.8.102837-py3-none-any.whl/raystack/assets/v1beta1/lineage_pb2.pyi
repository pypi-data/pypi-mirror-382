from raystack.assets.v1beta1 import resource_pb2 as _resource_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Lineage(_message.Message):
    __slots__ = ("upstreams", "downstreams")
    UPSTREAMS_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAMS_FIELD_NUMBER: _ClassVar[int]
    upstreams: _containers.RepeatedCompositeFieldContainer[_resource_pb2.Resource]
    downstreams: _containers.RepeatedCompositeFieldContainer[_resource_pb2.Resource]
    def __init__(self, upstreams: _Optional[_Iterable[_Union[_resource_pb2.Resource, _Mapping]]] = ..., downstreams: _Optional[_Iterable[_Union[_resource_pb2.Resource, _Mapping]]] = ...) -> None: ...
