import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from raystack.optimus.core.v1beta1 import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JobState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_STATE_UNSPECIFIED: _ClassVar[JobState]
    JOB_STATE_ENABLED: _ClassVar[JobState]
    JOB_STATE_DISABLED: _ClassVar[JobState]
JOB_STATE_UNSPECIFIED: JobState
JOB_STATE_ENABLED: JobState
JOB_STATE_DISABLED: JobState

class DeployJobSpecificationRequest(_message.Message):
    __slots__ = ("project_name", "jobs", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    JOBS_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    jobs: _containers.RepeatedCompositeFieldContainer[JobSpecification]
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., jobs: _Optional[_Iterable[_Union[JobSpecification, _Mapping]]] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class DeployJobSpecificationResponse(_message.Message):
    __slots__ = ("deployment_id", "log_status")
    DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LOG_STATUS_FIELD_NUMBER: _ClassVar[int]
    deployment_id: str
    log_status: _status_pb2.Log
    def __init__(self, deployment_id: _Optional[str] = ..., log_status: _Optional[_Union[_status_pb2.Log, _Mapping]] = ...) -> None: ...

class AddJobSpecificationsRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "specs")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    SPECS_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    specs: _containers.RepeatedCompositeFieldContainer[JobSpecification]
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., specs: _Optional[_Iterable[_Union[JobSpecification, _Mapping]]] = ...) -> None: ...

class AddJobSpecificationsResponse(_message.Message):
    __slots__ = ("log",)
    LOG_FIELD_NUMBER: _ClassVar[int]
    log: str
    def __init__(self, log: _Optional[str] = ...) -> None: ...

class UpdateJobSpecificationsRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "specs")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    SPECS_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    specs: _containers.RepeatedCompositeFieldContainer[JobSpecification]
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., specs: _Optional[_Iterable[_Union[JobSpecification, _Mapping]]] = ...) -> None: ...

class UpdateJobSpecificationsResponse(_message.Message):
    __slots__ = ("log",)
    LOG_FIELD_NUMBER: _ClassVar[int]
    log: str
    def __init__(self, log: _Optional[str] = ...) -> None: ...

class JobInspectRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "job_name", "spec", "scheduled_at")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_AT_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    job_name: str
    spec: JobSpecification
    scheduled_at: _timestamp_pb2.Timestamp
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., job_name: _Optional[str] = ..., spec: _Optional[_Union[JobSpecification, _Mapping]] = ..., scheduled_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class JobRun(_message.Message):
    __slots__ = ("state", "scheduled_at")
    STATE_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_AT_FIELD_NUMBER: _ClassVar[int]
    state: str
    scheduled_at: _timestamp_pb2.Timestamp
    def __init__(self, state: _Optional[str] = ..., scheduled_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class JobInspectResponse(_message.Message):
    __slots__ = ("basic_info", "upstreams", "downstreams")
    class BasicInfoSection(_message.Message):
        __slots__ = ("job", "source", "destination", "notice")
        JOB_FIELD_NUMBER: _ClassVar[int]
        SOURCE_FIELD_NUMBER: _ClassVar[int]
        DESTINATION_FIELD_NUMBER: _ClassVar[int]
        NOTICE_FIELD_NUMBER: _ClassVar[int]
        job: JobSpecification
        source: _containers.RepeatedScalarFieldContainer[str]
        destination: str
        notice: _containers.RepeatedCompositeFieldContainer[_status_pb2.Log]
        def __init__(self, job: _Optional[_Union[JobSpecification, _Mapping]] = ..., source: _Optional[_Iterable[str]] = ..., destination: _Optional[str] = ..., notice: _Optional[_Iterable[_Union[_status_pb2.Log, _Mapping]]] = ...) -> None: ...
    class JobDependency(_message.Message):
        __slots__ = ("name", "host", "project_name", "namespace_name", "task_name", "runs")
        NAME_FIELD_NUMBER: _ClassVar[int]
        HOST_FIELD_NUMBER: _ClassVar[int]
        PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
        NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
        TASK_NAME_FIELD_NUMBER: _ClassVar[int]
        RUNS_FIELD_NUMBER: _ClassVar[int]
        name: str
        host: str
        project_name: str
        namespace_name: str
        task_name: str
        runs: _containers.RepeatedCompositeFieldContainer[JobRun]
        def __init__(self, name: _Optional[str] = ..., host: _Optional[str] = ..., project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., task_name: _Optional[str] = ..., runs: _Optional[_Iterable[_Union[JobRun, _Mapping]]] = ...) -> None: ...
    class UpstreamSection(_message.Message):
        __slots__ = ("external_dependency", "internal_dependency", "http_dependency", "unknown_dependencies", "notice")
        class UnknownDependencies(_message.Message):
            __slots__ = ("job_name", "project_name", "resource_destination")
            JOB_NAME_FIELD_NUMBER: _ClassVar[int]
            PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
            RESOURCE_DESTINATION_FIELD_NUMBER: _ClassVar[int]
            job_name: str
            project_name: str
            resource_destination: str
            def __init__(self, job_name: _Optional[str] = ..., project_name: _Optional[str] = ..., resource_destination: _Optional[str] = ...) -> None: ...
        EXTERNAL_DEPENDENCY_FIELD_NUMBER: _ClassVar[int]
        INTERNAL_DEPENDENCY_FIELD_NUMBER: _ClassVar[int]
        HTTP_DEPENDENCY_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        NOTICE_FIELD_NUMBER: _ClassVar[int]
        external_dependency: _containers.RepeatedCompositeFieldContainer[JobInspectResponse.JobDependency]
        internal_dependency: _containers.RepeatedCompositeFieldContainer[JobInspectResponse.JobDependency]
        http_dependency: _containers.RepeatedCompositeFieldContainer[HttpDependency]
        unknown_dependencies: _containers.RepeatedCompositeFieldContainer[JobInspectResponse.UpstreamSection.UnknownDependencies]
        notice: _containers.RepeatedCompositeFieldContainer[_status_pb2.Log]
        def __init__(self, external_dependency: _Optional[_Iterable[_Union[JobInspectResponse.JobDependency, _Mapping]]] = ..., internal_dependency: _Optional[_Iterable[_Union[JobInspectResponse.JobDependency, _Mapping]]] = ..., http_dependency: _Optional[_Iterable[_Union[HttpDependency, _Mapping]]] = ..., unknown_dependencies: _Optional[_Iterable[_Union[JobInspectResponse.UpstreamSection.UnknownDependencies, _Mapping]]] = ..., notice: _Optional[_Iterable[_Union[_status_pb2.Log, _Mapping]]] = ...) -> None: ...
    class DownstreamSection(_message.Message):
        __slots__ = ("downstream_jobs", "notice")
        DOWNSTREAM_JOBS_FIELD_NUMBER: _ClassVar[int]
        NOTICE_FIELD_NUMBER: _ClassVar[int]
        downstream_jobs: _containers.RepeatedCompositeFieldContainer[JobInspectResponse.JobDependency]
        notice: _containers.RepeatedCompositeFieldContainer[_status_pb2.Log]
        def __init__(self, downstream_jobs: _Optional[_Iterable[_Union[JobInspectResponse.JobDependency, _Mapping]]] = ..., notice: _Optional[_Iterable[_Union[_status_pb2.Log, _Mapping]]] = ...) -> None: ...
    BASIC_INFO_FIELD_NUMBER: _ClassVar[int]
    UPSTREAMS_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAMS_FIELD_NUMBER: _ClassVar[int]
    basic_info: JobInspectResponse.BasicInfoSection
    upstreams: JobInspectResponse.UpstreamSection
    downstreams: JobInspectResponse.DownstreamSection
    def __init__(self, basic_info: _Optional[_Union[JobInspectResponse.BasicInfoSection, _Mapping]] = ..., upstreams: _Optional[_Union[JobInspectResponse.UpstreamSection, _Mapping]] = ..., downstreams: _Optional[_Union[JobInspectResponse.DownstreamSection, _Mapping]] = ...) -> None: ...

class CreateJobSpecificationRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "spec")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    spec: JobSpecification
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., spec: _Optional[_Union[JobSpecification, _Mapping]] = ...) -> None: ...

class CreateJobSpecificationResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...

class GetJobSpecificationRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "job_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    job_name: str
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., job_name: _Optional[str] = ...) -> None: ...

class GetJobSpecificationResponse(_message.Message):
    __slots__ = ("spec",)
    SPEC_FIELD_NUMBER: _ClassVar[int]
    spec: JobSpecification
    def __init__(self, spec: _Optional[_Union[JobSpecification, _Mapping]] = ...) -> None: ...

class DeleteJobSpecificationRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "job_name", "clean_history", "force")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    CLEAN_HISTORY_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    job_name: str
    clean_history: bool
    force: bool
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., job_name: _Optional[str] = ..., clean_history: _Optional[bool] = ..., force: _Optional[bool] = ...) -> None: ...

class DeleteJobSpecificationResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...

class ChangeJobNamespaceRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "job_name", "new_namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    NEW_NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    job_name: str
    new_namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., job_name: _Optional[str] = ..., new_namespace_name: _Optional[str] = ...) -> None: ...

class ChangeJobNamespaceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListJobSpecificationRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class ListJobSpecificationResponse(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[JobSpecification]
    def __init__(self, jobs: _Optional[_Iterable[_Union[JobSpecification, _Mapping]]] = ...) -> None: ...

class CheckJobSpecificationRequest(_message.Message):
    __slots__ = ("project_name", "job", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    job: JobSpecification
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., job: _Optional[_Union[JobSpecification, _Mapping]] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class CheckJobSpecificationResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: _Optional[bool] = ...) -> None: ...

class CheckJobSpecificationsRequest(_message.Message):
    __slots__ = ("project_name", "jobs", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    JOBS_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    jobs: _containers.RepeatedCompositeFieldContainer[JobSpecification]
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., jobs: _Optional[_Iterable[_Union[JobSpecification, _Mapping]]] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class CheckJobSpecificationsResponse(_message.Message):
    __slots__ = ("log_status",)
    LOG_STATUS_FIELD_NUMBER: _ClassVar[int]
    log_status: _status_pb2.Log
    def __init__(self, log_status: _Optional[_Union[_status_pb2.Log, _Mapping]] = ...) -> None: ...

class JobSpecification(_message.Message):
    __slots__ = ("version", "name", "owner", "start_date", "end_date", "interval", "depends_on_past", "catch_up", "task_name", "config", "window_size", "window_offset", "window_truncate_to", "dependencies", "assets", "hooks", "description", "labels", "behavior", "metadata", "destination", "sources")
    class AssetsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class Behavior(_message.Message):
        __slots__ = ("retry", "notify")
        class Retry(_message.Message):
            __slots__ = ("count", "delay", "exponential_backoff")
            COUNT_FIELD_NUMBER: _ClassVar[int]
            DELAY_FIELD_NUMBER: _ClassVar[int]
            EXPONENTIAL_BACKOFF_FIELD_NUMBER: _ClassVar[int]
            count: int
            delay: _duration_pb2.Duration
            exponential_backoff: bool
            def __init__(self, count: _Optional[int] = ..., delay: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., exponential_backoff: _Optional[bool] = ...) -> None: ...
        class Notifiers(_message.Message):
            __slots__ = ("on", "channels", "config")
            class ConfigEntry(_message.Message):
                __slots__ = ("key", "value")
                KEY_FIELD_NUMBER: _ClassVar[int]
                VALUE_FIELD_NUMBER: _ClassVar[int]
                key: str
                value: str
                def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
            ON_FIELD_NUMBER: _ClassVar[int]
            CHANNELS_FIELD_NUMBER: _ClassVar[int]
            CONFIG_FIELD_NUMBER: _ClassVar[int]
            on: JobEvent.Type
            channels: _containers.RepeatedScalarFieldContainer[str]
            config: _containers.ScalarMap[str, str]
            def __init__(self, on: _Optional[_Union[JobEvent.Type, str]] = ..., channels: _Optional[_Iterable[str]] = ..., config: _Optional[_Mapping[str, str]] = ...) -> None: ...
        RETRY_FIELD_NUMBER: _ClassVar[int]
        NOTIFY_FIELD_NUMBER: _ClassVar[int]
        retry: JobSpecification.Behavior.Retry
        notify: _containers.RepeatedCompositeFieldContainer[JobSpecification.Behavior.Notifiers]
        def __init__(self, retry: _Optional[_Union[JobSpecification.Behavior.Retry, _Mapping]] = ..., notify: _Optional[_Iterable[_Union[JobSpecification.Behavior.Notifiers, _Mapping]]] = ...) -> None: ...
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    DEPENDS_ON_PAST_FIELD_NUMBER: _ClassVar[int]
    CATCH_UP_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    WINDOW_SIZE_FIELD_NUMBER: _ClassVar[int]
    WINDOW_OFFSET_FIELD_NUMBER: _ClassVar[int]
    WINDOW_TRUNCATE_TO_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    HOOKS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    version: int
    name: str
    owner: str
    start_date: str
    end_date: str
    interval: str
    depends_on_past: bool
    catch_up: bool
    task_name: str
    config: _containers.RepeatedCompositeFieldContainer[JobConfigItem]
    window_size: str
    window_offset: str
    window_truncate_to: str
    dependencies: _containers.RepeatedCompositeFieldContainer[JobDependency]
    assets: _containers.ScalarMap[str, str]
    hooks: _containers.RepeatedCompositeFieldContainer[JobSpecHook]
    description: str
    labels: _containers.ScalarMap[str, str]
    behavior: JobSpecification.Behavior
    metadata: JobMetadata
    destination: str
    sources: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, version: _Optional[int] = ..., name: _Optional[str] = ..., owner: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., interval: _Optional[str] = ..., depends_on_past: _Optional[bool] = ..., catch_up: _Optional[bool] = ..., task_name: _Optional[str] = ..., config: _Optional[_Iterable[_Union[JobConfigItem, _Mapping]]] = ..., window_size: _Optional[str] = ..., window_offset: _Optional[str] = ..., window_truncate_to: _Optional[str] = ..., dependencies: _Optional[_Iterable[_Union[JobDependency, _Mapping]]] = ..., assets: _Optional[_Mapping[str, str]] = ..., hooks: _Optional[_Iterable[_Union[JobSpecHook, _Mapping]]] = ..., description: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., behavior: _Optional[_Union[JobSpecification.Behavior, _Mapping]] = ..., metadata: _Optional[_Union[JobMetadata, _Mapping]] = ..., destination: _Optional[str] = ..., sources: _Optional[_Iterable[str]] = ...) -> None: ...

class JobDependency(_message.Message):
    __slots__ = ("name", "type", "http_dependency")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    HTTP_DEPENDENCY_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    http_dependency: HttpDependency
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., http_dependency: _Optional[_Union[HttpDependency, _Mapping]] = ...) -> None: ...

class HttpDependency(_message.Message):
    __slots__ = ("name", "url", "headers", "params")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    headers: _containers.ScalarMap[str, str]
    params: _containers.ScalarMap[str, str]
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ..., headers: _Optional[_Mapping[str, str]] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class JobSpecHook(_message.Message):
    __slots__ = ("name", "config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    config: _containers.RepeatedCompositeFieldContainer[JobConfigItem]
    def __init__(self, name: _Optional[str] = ..., config: _Optional[_Iterable[_Union[JobConfigItem, _Mapping]]] = ...) -> None: ...

class JobConfigItem(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class JobEvent(_message.Message):
    __slots__ = ("type", "value")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[JobEvent.Type]
        TYPE_SLA_MISS: _ClassVar[JobEvent.Type]
        TYPE_JOB_SUCCESS: _ClassVar[JobEvent.Type]
        TYPE_FAILURE: _ClassVar[JobEvent.Type]
        TYPE_TASK_RETRY: _ClassVar[JobEvent.Type]
        TYPE_TASK_SUCCESS: _ClassVar[JobEvent.Type]
        TYPE_TASK_START: _ClassVar[JobEvent.Type]
        TYPE_TASK_FAIL: _ClassVar[JobEvent.Type]
        TYPE_SENSOR_RETRY: _ClassVar[JobEvent.Type]
        TYPE_SENSOR_SUCCESS: _ClassVar[JobEvent.Type]
        TYPE_SENSOR_START: _ClassVar[JobEvent.Type]
        TYPE_SENSOR_FAIL: _ClassVar[JobEvent.Type]
        TYPE_HOOK_START: _ClassVar[JobEvent.Type]
        TYPE_HOOK_RETRY: _ClassVar[JobEvent.Type]
        TYPE_HOOK_FAIL: _ClassVar[JobEvent.Type]
        TYPE_HOOK_SUCCESS: _ClassVar[JobEvent.Type]
    TYPE_UNSPECIFIED: JobEvent.Type
    TYPE_SLA_MISS: JobEvent.Type
    TYPE_JOB_SUCCESS: JobEvent.Type
    TYPE_FAILURE: JobEvent.Type
    TYPE_TASK_RETRY: JobEvent.Type
    TYPE_TASK_SUCCESS: JobEvent.Type
    TYPE_TASK_START: JobEvent.Type
    TYPE_TASK_FAIL: JobEvent.Type
    TYPE_SENSOR_RETRY: JobEvent.Type
    TYPE_SENSOR_SUCCESS: JobEvent.Type
    TYPE_SENSOR_START: JobEvent.Type
    TYPE_SENSOR_FAIL: JobEvent.Type
    TYPE_HOOK_START: JobEvent.Type
    TYPE_HOOK_RETRY: JobEvent.Type
    TYPE_HOOK_FAIL: JobEvent.Type
    TYPE_HOOK_SUCCESS: JobEvent.Type
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: JobEvent.Type
    value: _struct_pb2.Struct
    def __init__(self, type: _Optional[_Union[JobEvent.Type, str]] = ..., value: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class JobMetadata(_message.Message):
    __slots__ = ("resource", "airflow")
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_FIELD_NUMBER: _ClassVar[int]
    resource: JobSpecMetadataResource
    airflow: JobSpecMetadataAirflow
    def __init__(self, resource: _Optional[_Union[JobSpecMetadataResource, _Mapping]] = ..., airflow: _Optional[_Union[JobSpecMetadataAirflow, _Mapping]] = ...) -> None: ...

class JobSpecMetadataResource(_message.Message):
    __slots__ = ("request", "limit")
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    request: JobSpecMetadataResourceConfig
    limit: JobSpecMetadataResourceConfig
    def __init__(self, request: _Optional[_Union[JobSpecMetadataResourceConfig, _Mapping]] = ..., limit: _Optional[_Union[JobSpecMetadataResourceConfig, _Mapping]] = ...) -> None: ...

class JobSpecMetadataResourceConfig(_message.Message):
    __slots__ = ("cpu", "memory")
    CPU_FIELD_NUMBER: _ClassVar[int]
    MEMORY_FIELD_NUMBER: _ClassVar[int]
    cpu: str
    memory: str
    def __init__(self, cpu: _Optional[str] = ..., memory: _Optional[str] = ...) -> None: ...

class JobSpecMetadataAirflow(_message.Message):
    __slots__ = ("pool", "queue")
    POOL_FIELD_NUMBER: _ClassVar[int]
    QUEUE_FIELD_NUMBER: _ClassVar[int]
    pool: str
    queue: str
    def __init__(self, pool: _Optional[str] = ..., queue: _Optional[str] = ...) -> None: ...

class RefreshJobsRequest(_message.Message):
    __slots__ = ("project_name", "namespace_names", "job_names")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAMES_FIELD_NUMBER: _ClassVar[int]
    JOB_NAMES_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_names: _containers.RepeatedScalarFieldContainer[str]
    job_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_name: _Optional[str] = ..., namespace_names: _Optional[_Iterable[str]] = ..., job_names: _Optional[_Iterable[str]] = ...) -> None: ...

class RefreshJobsResponse(_message.Message):
    __slots__ = ("log_status",)
    LOG_STATUS_FIELD_NUMBER: _ClassVar[int]
    log_status: _status_pb2.Log
    def __init__(self, log_status: _Optional[_Union[_status_pb2.Log, _Mapping]] = ...) -> None: ...

class GetDeployJobsStatusRequest(_message.Message):
    __slots__ = ("deploy_id",)
    DEPLOY_ID_FIELD_NUMBER: _ClassVar[int]
    deploy_id: str
    def __init__(self, deploy_id: _Optional[str] = ...) -> None: ...

class GetDeployJobsStatusResponse(_message.Message):
    __slots__ = ("status", "failures", "success_count", "failure_count", "unknown_dependencies")
    class UnknownDependenciesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FAILURES_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_COUNT_FIELD_NUMBER: _ClassVar[int]
    FAILURE_COUNT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    status: str
    failures: _containers.RepeatedCompositeFieldContainer[DeployJobFailure]
    success_count: int
    failure_count: int
    unknown_dependencies: _containers.ScalarMap[str, str]
    def __init__(self, status: _Optional[str] = ..., failures: _Optional[_Iterable[_Union[DeployJobFailure, _Mapping]]] = ..., success_count: _Optional[int] = ..., failure_count: _Optional[int] = ..., unknown_dependencies: _Optional[_Mapping[str, str]] = ...) -> None: ...

class DeployJobFailure(_message.Message):
    __slots__ = ("job_name", "message")
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    job_name: str
    message: str
    def __init__(self, job_name: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class GetJobSpecificationsRequest(_message.Message):
    __slots__ = ("project_name", "resource_destination", "job_name", "namespace_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_DESTINATION_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    resource_destination: str
    job_name: str
    namespace_name: str
    def __init__(self, project_name: _Optional[str] = ..., resource_destination: _Optional[str] = ..., job_name: _Optional[str] = ..., namespace_name: _Optional[str] = ...) -> None: ...

class GetJobSpecificationsResponse(_message.Message):
    __slots__ = ("jobs", "job_specification_responses")
    JOBS_FIELD_NUMBER: _ClassVar[int]
    JOB_SPECIFICATION_RESPONSES_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[JobSpecification]
    job_specification_responses: _containers.RepeatedCompositeFieldContainer[JobSpecificationResponse]
    def __init__(self, jobs: _Optional[_Iterable[_Union[JobSpecification, _Mapping]]] = ..., job_specification_responses: _Optional[_Iterable[_Union[JobSpecificationResponse, _Mapping]]] = ...) -> None: ...

class JobSpecificationResponse(_message.Message):
    __slots__ = ("project_name", "namespace_name", "job")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    job: JobSpecification
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., job: _Optional[_Union[JobSpecification, _Mapping]] = ...) -> None: ...

class ReplaceAllJobSpecificationsRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "jobs")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOBS_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    jobs: _containers.RepeatedCompositeFieldContainer[JobSpecification]
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., jobs: _Optional[_Iterable[_Union[JobSpecification, _Mapping]]] = ...) -> None: ...

class ReplaceAllJobSpecificationsResponse(_message.Message):
    __slots__ = ("log_status",)
    LOG_STATUS_FIELD_NUMBER: _ClassVar[int]
    log_status: _status_pb2.Log
    def __init__(self, log_status: _Optional[_Union[_status_pb2.Log, _Mapping]] = ...) -> None: ...

class GetJobTaskRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "job_name")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    job_name: str
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., job_name: _Optional[str] = ...) -> None: ...

class GetJobTaskResponse(_message.Message):
    __slots__ = ("task",)
    TASK_FIELD_NUMBER: _ClassVar[int]
    task: JobTask
    def __init__(self, task: _Optional[_Union[JobTask, _Mapping]] = ...) -> None: ...

class JobTask(_message.Message):
    __slots__ = ("name", "description", "image", "destination", "dependencies")
    class Destination(_message.Message):
        __slots__ = ("destination", "type")
        DESTINATION_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        destination: str
        type: str
        def __init__(self, destination: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...
    class Dependency(_message.Message):
        __slots__ = ("dependency",)
        DEPENDENCY_FIELD_NUMBER: _ClassVar[int]
        dependency: str
        def __init__(self, dependency: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    image: str
    destination: JobTask.Destination
    dependencies: _containers.RepeatedCompositeFieldContainer[JobTask.Dependency]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., image: _Optional[str] = ..., destination: _Optional[_Union[JobTask.Destination, _Mapping]] = ..., dependencies: _Optional[_Iterable[_Union[JobTask.Dependency, _Mapping]]] = ...) -> None: ...

class GetWindowRequest(_message.Message):
    __slots__ = ("scheduled_at", "size", "offset", "truncate_to", "version")
    SCHEDULED_AT_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TRUNCATE_TO_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    scheduled_at: _timestamp_pb2.Timestamp
    size: str
    offset: str
    truncate_to: str
    version: int
    def __init__(self, scheduled_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., size: _Optional[str] = ..., offset: _Optional[str] = ..., truncate_to: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class GetWindowResponse(_message.Message):
    __slots__ = ("start", "end")
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    def __init__(self, start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UpdateJobsStateRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "remark", "state", "job_names")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    REMARK_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    JOB_NAMES_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    remark: str
    state: JobState
    job_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., remark: _Optional[str] = ..., state: _Optional[_Union[JobState, str]] = ..., job_names: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateJobsStateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SyncJobsStateRequest(_message.Message):
    __slots__ = ("project_name", "namespace_name", "job_states")
    class JobStatePair(_message.Message):
        __slots__ = ("job_name", "state")
        JOB_NAME_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        job_name: str
        state: JobState
        def __init__(self, job_name: _Optional[str] = ..., state: _Optional[_Union[JobState, str]] = ...) -> None: ...
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_STATES_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    namespace_name: str
    job_states: _containers.RepeatedCompositeFieldContainer[SyncJobsStateRequest.JobStatePair]
    def __init__(self, project_name: _Optional[str] = ..., namespace_name: _Optional[str] = ..., job_states: _Optional[_Iterable[_Union[SyncJobsStateRequest.JobStatePair, _Mapping]]] = ...) -> None: ...

class SyncJobsStateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
