import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from raystack.optimus.core.v1beta1 import job_spec_pb2 as _job_spec_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UploadToSchedulerRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class UploadToSchedulerResponse(_message.Message):
    __slots__ = ("status", "error_message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: bool
    error_message: str
    def __init__(self, status: _Optional[bool] = ..., error_message: _Optional[str] = ...) -> None: ...

class RegisterJobEventRequest(_message.Message):
    __slots__ = ("project_name", "job_name", "namespace_name", "event")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    job_name: str
    namespace_name: str
    event: _job_spec_pb2.JobEvent
    def __init__(self, project_name: _Optional[str] = ..., job_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., event: _Optional[_Union[_job_spec_pb2.JobEvent, _Mapping]] = ...) -> None: ...

class RegisterJobEventResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class JobRunInputRequest(_message.Message):
    __slots__ = ("project_name", "job_name", "scheduled_at", "instance_name", "instance_type", "jobrun_id")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_AT_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    JOBRUN_ID_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    job_name: str
    scheduled_at: _timestamp_pb2.Timestamp
    instance_name: str
    instance_type: InstanceSpec.Type
    jobrun_id: str
    def __init__(self, project_name: _Optional[str] = ..., job_name: _Optional[str] = ..., scheduled_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., instance_name: _Optional[str] = ..., instance_type: _Optional[_Union[InstanceSpec.Type, str]] = ..., jobrun_id: _Optional[str] = ...) -> None: ...

class JobRunRequest(_message.Message):
    __slots__ = ("project_name", "job_name", "start_date", "end_date", "filter")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    job_name: str
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    filter: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_name: _Optional[str] = ..., job_name: _Optional[str] = ..., start_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., filter: _Optional[_Iterable[str]] = ...) -> None: ...

class JobRunResponse(_message.Message):
    __slots__ = ("job_runs",)
    JOB_RUNS_FIELD_NUMBER: _ClassVar[int]
    job_runs: _containers.RepeatedCompositeFieldContainer[_job_spec_pb2.JobRun]
    def __init__(self, job_runs: _Optional[_Iterable[_Union[_job_spec_pb2.JobRun, _Mapping]]] = ...) -> None: ...

class InstanceSpec(_message.Message):
    __slots__ = ("state", "data", "executed_at", "name", "type")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[InstanceSpec.Type]
        TYPE_TASK: _ClassVar[InstanceSpec.Type]
        TYPE_HOOK: _ClassVar[InstanceSpec.Type]
    TYPE_UNSPECIFIED: InstanceSpec.Type
    TYPE_TASK: InstanceSpec.Type
    TYPE_HOOK: InstanceSpec.Type
    STATE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    EXECUTED_AT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    state: str
    data: _containers.RepeatedCompositeFieldContainer[InstanceSpecData]
    executed_at: _timestamp_pb2.Timestamp
    name: str
    type: InstanceSpec.Type
    def __init__(self, state: _Optional[str] = ..., data: _Optional[_Iterable[_Union[InstanceSpecData, _Mapping]]] = ..., executed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ..., type: _Optional[_Union[InstanceSpec.Type, str]] = ...) -> None: ...

class InstanceSpecData(_message.Message):
    __slots__ = ("name", "value", "type")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[InstanceSpecData.Type]
        TYPE_ENV: _ClassVar[InstanceSpecData.Type]
        TYPE_FILE: _ClassVar[InstanceSpecData.Type]
    TYPE_UNSPECIFIED: InstanceSpecData.Type
    TYPE_ENV: InstanceSpecData.Type
    TYPE_FILE: InstanceSpecData.Type
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    type: InstanceSpecData.Type
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., type: _Optional[_Union[InstanceSpecData.Type, str]] = ...) -> None: ...

class JobRunInputResponse(_message.Message):
    __slots__ = ("envs", "files", "secrets")
    class EnvsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class FilesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class SecretsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ENVS_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    envs: _containers.ScalarMap[str, str]
    files: _containers.ScalarMap[str, str]
    secrets: _containers.ScalarMap[str, str]
    def __init__(self, envs: _Optional[_Mapping[str, str]] = ..., files: _Optional[_Mapping[str, str]] = ..., secrets: _Optional[_Mapping[str, str]] = ...) -> None: ...

class TaskWindow(_message.Message):
    __slots__ = ("size", "offset", "truncate_to")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TRUNCATE_TO_FIELD_NUMBER: _ClassVar[int]
    size: _duration_pb2.Duration
    offset: _duration_pb2.Duration
    truncate_to: str
    def __init__(self, size: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., offset: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., truncate_to: _Optional[str] = ...) -> None: ...
