import datetime

from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelSignature(_message.Message):
    __slots__ = ("inputs", "outputs")
    class Parameter(_message.Message):
        __slots__ = ("name", "data_type", "shape")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
        SHAPE_FIELD_NUMBER: _ClassVar[int]
        name: str
        data_type: str
        shape: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, name: _Optional[str] = ..., data_type: _Optional[str] = ..., shape: _Optional[_Iterable[int]] = ...) -> None: ...
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    inputs: _containers.RepeatedCompositeFieldContainer[ModelSignature.Parameter]
    outputs: _containers.RepeatedCompositeFieldContainer[ModelSignature.Parameter]
    def __init__(self, inputs: _Optional[_Iterable[_Union[ModelSignature.Parameter, _Mapping]]] = ..., outputs: _Optional[_Iterable[_Union[ModelSignature.Parameter, _Mapping]]] = ...) -> None: ...

class ModelVersion(_message.Message):
    __slots__ = ("signature", "status", "version", "attributes", "labels", "create_time", "update_time")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    signature: ModelSignature
    status: str
    version: str
    attributes: _struct_pb2.Struct
    labels: _containers.ScalarMap[str, str]
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    def __init__(self, signature: _Optional[_Union[ModelSignature, _Mapping]] = ..., status: _Optional[str] = ..., version: _Optional[str] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., labels: _Optional[_Mapping[str, str]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Model(_message.Message):
    __slots__ = ("namespace", "flavor", "algorithm", "status", "versions", "attributes", "create_time", "update_time")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    FLAVOR_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSIONS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    flavor: str
    algorithm: str
    status: str
    versions: _containers.RepeatedCompositeFieldContainer[ModelVersion]
    attributes: _struct_pb2.Struct
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    def __init__(self, namespace: _Optional[str] = ..., flavor: _Optional[str] = ..., algorithm: _Optional[str] = ..., status: _Optional[str] = ..., versions: _Optional[_Iterable[_Union[ModelVersion, _Mapping]]] = ..., attributes: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
