from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Level(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LEVEL_UNSPECIFIED: _ClassVar[Level]
    LEVEL_TRACE: _ClassVar[Level]
    LEVEL_DEBUG: _ClassVar[Level]
    LEVEL_INFO: _ClassVar[Level]
    LEVEL_WARNING: _ClassVar[Level]
    LEVEL_ERROR: _ClassVar[Level]
    LEVEL_FATAL: _ClassVar[Level]
LEVEL_UNSPECIFIED: Level
LEVEL_TRACE: Level
LEVEL_DEBUG: Level
LEVEL_INFO: Level
LEVEL_WARNING: Level
LEVEL_ERROR: Level
LEVEL_FATAL: Level

class Log(_message.Message):
    __slots__ = ("level", "message")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    level: Level
    message: str
    def __init__(self, level: _Optional[_Union[Level, str]] = ..., message: _Optional[str] = ...) -> None: ...
