from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ConnectorInformation(_message.Message):
    __slots__ = ("connected", "connected_since", "latency", "healthy")
    CONNECTED_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_SINCE_FIELD_NUMBER: _ClassVar[int]
    LATENCY_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    connected: bool
    connected_since: int
    latency: int
    healthy: bool
    def __init__(self, connected: bool = ..., connected_since: _Optional[int] = ..., latency: _Optional[int] = ..., healthy: bool = ...) -> None: ...
