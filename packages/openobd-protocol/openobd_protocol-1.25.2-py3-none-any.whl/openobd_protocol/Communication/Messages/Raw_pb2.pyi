from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RawFrame(_message.Message):
    __slots__ = ("channel", "payload")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    channel: RawChannel
    payload: str
    def __init__(self, channel: _Optional[_Union[RawChannel, _Mapping]] = ..., payload: _Optional[str] = ...) -> None: ...

class RawChannel(_message.Message):
    __slots__ = ("bus_name", "request_id", "response_id")
    BUS_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    bus_name: str
    request_id: int
    response_id: int
    def __init__(self, bus_name: _Optional[str] = ..., request_id: _Optional[int] = ..., response_id: _Optional[int] = ...) -> None: ...
