from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskIndex(_message.Message):
    __slots__ = ("int_value", "string_value")
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    int_value: int
    string_value: str
    def __init__(self, int_value: _Optional[int] = ..., string_value: _Optional[str] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ("role", "text", "parts", "tool_calls", "name", "tool_call_id")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    role: str
    text: str
    parts: _struct_pb2.ListValue
    tool_calls: _struct_pb2.ListValue
    name: _struct_pb2.Value
    tool_call_id: _struct_pb2.Value
    def __init__(self, role: _Optional[str] = ..., text: _Optional[str] = ..., parts: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ..., tool_calls: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ..., name: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., tool_call_id: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
