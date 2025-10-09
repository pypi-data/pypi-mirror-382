import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListReplayRequest(_message.Message):
    __slots__ = ("project_name",)
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    def __init__(self, project_name: _Optional[str] = ...) -> None: ...

class ListReplayResponse(_message.Message):
    __slots__ = ("replays",)
    REPLAYS_FIELD_NUMBER: _ClassVar[int]
    replays: _containers.RepeatedCompositeFieldContainer[GetReplayResponse]
    def __init__(self, replays: _Optional[_Iterable[_Union[GetReplayResponse, _Mapping]]] = ...) -> None: ...

class GetReplayRequest(_message.Message):
    __slots__ = ("replay_id", "project_name")
    REPLAY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    replay_id: str
    project_name: str
    def __init__(self, replay_id: _Optional[str] = ..., project_name: _Optional[str] = ...) -> None: ...

class GetReplayResponse(_message.Message):
    __slots__ = ("id", "job_name", "status", "replay_config", "replay_runs")
    ID_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REPLAY_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REPLAY_RUNS_FIELD_NUMBER: _ClassVar[int]
    id: str
    job_name: str
    status: str
    replay_config: ReplayConfig
    replay_runs: _containers.RepeatedCompositeFieldContainer[ReplayRun]
    def __init__(self, id: _Optional[str] = ..., job_name: _Optional[str] = ..., status: _Optional[str] = ..., replay_config: _Optional[_Union[ReplayConfig, _Mapping]] = ..., replay_runs: _Optional[_Iterable[_Union[ReplayRun, _Mapping]]] = ...) -> None: ...

class ReplayConfig(_message.Message):
    __slots__ = ("start_time", "end_time", "parallel", "job_config", "description")
    class JobConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_FIELD_NUMBER: _ClassVar[int]
    JOB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    parallel: bool
    job_config: _containers.ScalarMap[str, str]
    description: str
    def __init__(self, start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., parallel: _Optional[bool] = ..., job_config: _Optional[_Mapping[str, str]] = ..., description: _Optional[str] = ...) -> None: ...

class ReplayRun(_message.Message):
    __slots__ = ("scheduled_at", "status")
    SCHEDULED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    scheduled_at: _timestamp_pb2.Timestamp
    status: str
    def __init__(self, scheduled_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ...) -> None: ...

class ReplayDryRunResponse(_message.Message):
    __slots__ = ("replay_runs",)
    REPLAY_RUNS_FIELD_NUMBER: _ClassVar[int]
    replay_runs: _containers.RepeatedCompositeFieldContainer[ReplayRun]
    def __init__(self, replay_runs: _Optional[_Iterable[_Union[ReplayRun, _Mapping]]] = ...) -> None: ...

class ReplayRequest(_message.Message):
    __slots__ = ("project_name", "job_name", "namespace_name", "start_time", "end_time", "parallel", "description", "job_config")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    JOB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    job_name: str
    namespace_name: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    parallel: bool
    description: str
    job_config: str
    def __init__(self, project_name: _Optional[str] = ..., job_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., parallel: _Optional[bool] = ..., description: _Optional[str] = ..., job_config: _Optional[str] = ...) -> None: ...

class ReplayDryRunRequest(_message.Message):
    __slots__ = ("project_name", "job_name", "namespace_name", "start_time", "end_time", "parallel", "description", "job_config")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    JOB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    job_name: str
    namespace_name: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    parallel: bool
    description: str
    job_config: str
    def __init__(self, project_name: _Optional[str] = ..., job_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., parallel: _Optional[bool] = ..., description: _Optional[str] = ..., job_config: _Optional[str] = ...) -> None: ...

class ReplayResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...
