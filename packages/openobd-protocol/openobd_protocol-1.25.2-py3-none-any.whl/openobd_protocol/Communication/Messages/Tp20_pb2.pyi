from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Tp20Message(_message.Message):
    __slots__ = ("channel", "payload")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    channel: Tp20Channel
    payload: str
    def __init__(self, channel: _Optional[_Union[Tp20Channel, _Mapping]] = ..., payload: _Optional[str] = ...) -> None: ...

class Tp20Channel(_message.Message):
    __slots__ = ("bus_name", "logical_address")
    BUS_NAME_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    bus_name: str
    logical_address: int
    def __init__(self, bus_name: _Optional[str] = ..., logical_address: _Optional[int] = ...) -> None: ...
