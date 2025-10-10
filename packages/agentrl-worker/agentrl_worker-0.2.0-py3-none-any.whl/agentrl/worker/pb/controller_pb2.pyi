from google.protobuf import timestamp_pb2 as _timestamp_pb2
import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReceiveHeartbeatRequest(_message.Message):
    __slots__ = ("id", "name", "concurrency", "indices")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONCURRENCY_FIELD_NUMBER: _ClassVar[int]
    INDICES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    concurrency: int
    indices: _containers.RepeatedCompositeFieldContainer[_common_pb2.TaskIndex]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., concurrency: _Optional[int] = ..., indices: _Optional[_Iterable[_Union[_common_pb2.TaskIndex, _Mapping]]] = ...) -> None: ...

class SessionCancelNotice(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: int
    def __init__(self, session_id: _Optional[int] = ...) -> None: ...

class WorkerStreamEnvelope(_message.Message):
    __slots__ = ("id", "type", "timestamp", "receive_heartbeat_request", "session_cancel_notice", "worker_request", "worker_response")
    class MessageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HEARTBEAT: _ClassVar[WorkerStreamEnvelope.MessageType]
        REQUEST: _ClassVar[WorkerStreamEnvelope.MessageType]
        RESPONSE: _ClassVar[WorkerStreamEnvelope.MessageType]
    HEARTBEAT: WorkerStreamEnvelope.MessageType
    REQUEST: WorkerStreamEnvelope.MessageType
    RESPONSE: WorkerStreamEnvelope.MessageType
    class WorkerRequest(_message.Message):
        __slots__ = ("method", "endpoint", "json")
        METHOD_FIELD_NUMBER: _ClassVar[int]
        ENDPOINT_FIELD_NUMBER: _ClassVar[int]
        JSON_FIELD_NUMBER: _ClassVar[int]
        method: str
        endpoint: str
        json: bytes
        def __init__(self, method: _Optional[str] = ..., endpoint: _Optional[str] = ..., json: _Optional[bytes] = ...) -> None: ...
    class WorkerResponse(_message.Message):
        __slots__ = ("code", "message", "json")
        CODE_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        JSON_FIELD_NUMBER: _ClassVar[int]
        code: int
        message: str
        json: bytes
        def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., json: _Optional[bytes] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RECEIVE_HEARTBEAT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SESSION_CANCEL_NOTICE_FIELD_NUMBER: _ClassVar[int]
    WORKER_REQUEST_FIELD_NUMBER: _ClassVar[int]
    WORKER_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: WorkerStreamEnvelope.MessageType
    timestamp: _timestamp_pb2.Timestamp
    receive_heartbeat_request: ReceiveHeartbeatRequest
    session_cancel_notice: SessionCancelNotice
    worker_request: WorkerStreamEnvelope.WorkerRequest
    worker_response: WorkerStreamEnvelope.WorkerResponse
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[WorkerStreamEnvelope.MessageType, str]] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., receive_heartbeat_request: _Optional[_Union[ReceiveHeartbeatRequest, _Mapping]] = ..., session_cancel_notice: _Optional[_Union[SessionCancelNotice, _Mapping]] = ..., worker_request: _Optional[_Union[WorkerStreamEnvelope.WorkerRequest, _Mapping]] = ..., worker_response: _Optional[_Union[WorkerStreamEnvelope.WorkerResponse, _Mapping]] = ...) -> None: ...
