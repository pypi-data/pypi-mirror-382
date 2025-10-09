import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from raystack.optimus.core.v1beta1 import job_spec_pb2 as _job_spec_pb2
from raystack.optimus.core.v1beta1 import resource_pb2 as _resource_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceChangePayload(_message.Message):
    __slots__ = ("datastore_name", "resource")
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    datastore_name: str
    resource: _resource_pb2.ResourceSpecification
    def __init__(self, datastore_name: _Optional[str] = ..., resource: _Optional[_Union[_resource_pb2.ResourceSpecification, _Mapping]] = ...) -> None: ...

class JobChangePayload(_message.Message):
    __slots__ = ("job_name", "job_spec")
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_SPEC_FIELD_NUMBER: _ClassVar[int]
    job_name: str
    job_spec: _job_spec_pb2.JobSpecification
    def __init__(self, job_name: _Optional[str] = ..., job_spec: _Optional[_Union[_job_spec_pb2.JobSpecification, _Mapping]] = ...) -> None: ...

class JobRunPayload(_message.Message):
    __slots__ = ("job_name", "scheduled_at", "job_run_id", "start_time")
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_AT_FIELD_NUMBER: _ClassVar[int]
    JOB_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    job_name: str
    scheduled_at: _timestamp_pb2.Timestamp
    job_run_id: str
    start_time: _timestamp_pb2.Timestamp
    def __init__(self, job_name: _Optional[str] = ..., scheduled_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., job_run_id: _Optional[str] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class JobStateChangePayload(_message.Message):
    __slots__ = ("job_name", "state")
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    job_name: str
    state: _job_spec_pb2.JobState
    def __init__(self, job_name: _Optional[str] = ..., state: _Optional[_Union[_job_spec_pb2.JobState, str]] = ...) -> None: ...

class OptimusChangeEvent(_message.Message):
    __slots__ = ("event_id", "occurred_at", "project_name", "namespace_name", "event_type", "job_change", "resource_change", "job_run", "job_state_change")
    class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        EVENT_TYPE_TYPE_UNSPECIFIED: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_RESOURCE_CREATE: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_RESOURCE_UPDATE: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_JOB_CREATE: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_JOB_UPDATE: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_JOB_DELETE: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_JOB_WAIT_UPSTREAM: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_JOB_IN_PROGRESS: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_JOB_SUCCESS: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_JOB_FAILURE: _ClassVar[OptimusChangeEvent.EventType]
        EVENT_TYPE_JOB_STATE_CHANGE: _ClassVar[OptimusChangeEvent.EventType]
    EVENT_TYPE_TYPE_UNSPECIFIED: OptimusChangeEvent.EventType
    EVENT_TYPE_RESOURCE_CREATE: OptimusChangeEvent.EventType
    EVENT_TYPE_RESOURCE_UPDATE: OptimusChangeEvent.EventType
    EVENT_TYPE_JOB_CREATE: OptimusChangeEvent.EventType
    EVENT_TYPE_JOB_UPDATE: OptimusChangeEvent.EventType
    EVENT_TYPE_JOB_DELETE: OptimusChangeEvent.EventType
    EVENT_TYPE_JOB_WAIT_UPSTREAM: OptimusChangeEvent.EventType
    EVENT_TYPE_JOB_IN_PROGRESS: OptimusChangeEvent.EventType
    EVENT_TYPE_JOB_SUCCESS: OptimusChangeEvent.EventType
    EVENT_TYPE_JOB_FAILURE: OptimusChangeEvent.EventType
    EVENT_TYPE_JOB_STATE_CHANGE: OptimusChangeEvent.EventType
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_AT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    JOB_CHANGE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_CHANGE_FIELD_NUMBER: _ClassVar[int]
    JOB_RUN_FIELD_NUMBER: _ClassVar[int]
    JOB_STATE_CHANGE_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    occurred_at: _timestamp_pb2.Timestamp
    project_name: str
    namespace_name: str
    event_type: OptimusChangeEvent.EventType
    job_change: JobChangePayload
    resource_change: ResourceChangePayload
    job_run: JobRunPayload
    job_state_change: JobStateChangePayload
    def __init__(self, event_id: _Optional[str] = ..., occurred_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., event_type: _Optional[_Union[OptimusChangeEvent.EventType, str]] = ..., job_change: _Optional[_Union[JobChangePayload, _Mapping]] = ..., resource_change: _Optional[_Union[ResourceChangePayload, _Mapping]] = ..., job_run: _Optional[_Union[JobRunPayload, _Mapping]] = ..., job_state_change: _Optional[_Union[JobStateChangePayload, _Mapping]] = ...) -> None: ...
