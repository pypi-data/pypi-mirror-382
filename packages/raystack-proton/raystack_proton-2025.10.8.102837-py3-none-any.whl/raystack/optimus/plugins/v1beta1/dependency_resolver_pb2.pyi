import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetNameRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNameResponse(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GenerateDestinationRequest(_message.Message):
    __slots__ = ("config", "assets", "options")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    config: Configs
    assets: Assets
    options: PluginOptions
    def __init__(self, config: _Optional[_Union[Configs, _Mapping]] = ..., assets: _Optional[_Union[Assets, _Mapping]] = ..., options: _Optional[_Union[PluginOptions, _Mapping]] = ...) -> None: ...

class GenerateDestinationResponse(_message.Message):
    __slots__ = ("destination", "destination_type")
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    destination: str
    destination_type: str
    def __init__(self, destination: _Optional[str] = ..., destination_type: _Optional[str] = ...) -> None: ...

class GenerateDependenciesRequest(_message.Message):
    __slots__ = ("config", "assets", "options")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    config: Configs
    assets: Assets
    options: PluginOptions
    def __init__(self, config: _Optional[_Union[Configs, _Mapping]] = ..., assets: _Optional[_Union[Assets, _Mapping]] = ..., options: _Optional[_Union[PluginOptions, _Mapping]] = ...) -> None: ...

class GenerateDependenciesResponse(_message.Message):
    __slots__ = ("dependencies",)
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    dependencies: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, dependencies: _Optional[_Iterable[str]] = ...) -> None: ...

class Configs(_message.Message):
    __slots__ = ("configs",)
    class Config(_message.Message):
        __slots__ = ("name", "value")
        NAME_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        name: str
        value: str
        def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    configs: _containers.RepeatedCompositeFieldContainer[Configs.Config]
    def __init__(self, configs: _Optional[_Iterable[_Union[Configs.Config, _Mapping]]] = ...) -> None: ...

class Assets(_message.Message):
    __slots__ = ("assets",)
    class Asset(_message.Message):
        __slots__ = ("name", "value")
        NAME_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        name: str
        value: str
        def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    assets: _containers.RepeatedCompositeFieldContainer[Assets.Asset]
    def __init__(self, assets: _Optional[_Iterable[_Union[Assets.Asset, _Mapping]]] = ...) -> None: ...

class InstanceData(_message.Message):
    __slots__ = ("name", "value", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    type: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class CompileAssetsRequest(_message.Message):
    __slots__ = ("configs", "assets", "instance_data", "start_time", "end_time", "options")
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_DATA_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    configs: Configs
    assets: Assets
    instance_data: _containers.RepeatedCompositeFieldContainer[InstanceData]
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    options: PluginOptions
    def __init__(self, configs: _Optional[_Union[Configs, _Mapping]] = ..., assets: _Optional[_Union[Assets, _Mapping]] = ..., instance_data: _Optional[_Iterable[_Union[InstanceData, _Mapping]]] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., options: _Optional[_Union[PluginOptions, _Mapping]] = ...) -> None: ...

class CompileAssetsResponse(_message.Message):
    __slots__ = ("assets",)
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    assets: Assets
    def __init__(self, assets: _Optional[_Union[Assets, _Mapping]] = ...) -> None: ...

class PluginOptions(_message.Message):
    __slots__ = ("dry_run",)
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    dry_run: bool
    def __init__(self, dry_run: _Optional[bool] = ...) -> None: ...
