from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TicketId(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class ConnectorId(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class SessionInfo(_message.Message):
    __slots__ = ("id", "state", "created_at", "grpc_endpoint", "authentication_token")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    GRPC_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: str
    created_at: str
    grpc_endpoint: str
    authentication_token: str
    def __init__(self, id: _Optional[str] = ..., state: _Optional[str] = ..., created_at: _Optional[str] = ..., grpc_endpoint: _Optional[str] = ..., authentication_token: _Optional[str] = ...) -> None: ...

class Authenticate(_message.Message):
    __slots__ = ("client_id", "client_secret", "cluster_id")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    client_secret: str
    cluster_id: str
    def __init__(self, client_id: _Optional[str] = ..., client_secret: _Optional[str] = ..., cluster_id: _Optional[str] = ...) -> None: ...

class SessionControllerToken(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class SessionInfoList(_message.Message):
    __slots__ = ("sessions",)
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedCompositeFieldContainer[SessionInfo]
    def __init__(self, sessions: _Optional[_Iterable[_Union[SessionInfo, _Mapping]]] = ...) -> None: ...

class SessionId(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...
