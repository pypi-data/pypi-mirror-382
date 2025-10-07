from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DoipMessage(_message.Message):
    __slots__ = ("channel", "payload")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    channel: DoipChannel
    payload: str
    def __init__(self, channel: _Optional[_Union[DoipChannel, _Mapping]] = ..., payload: _Optional[str] = ...) -> None: ...

class DoipChannel(_message.Message):
    __slots__ = ("bus_name", "gateway_id", "tester_id", "ecu_id")
    BUS_NAME_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    TESTER_ID_FIELD_NUMBER: _ClassVar[int]
    ECU_ID_FIELD_NUMBER: _ClassVar[int]
    bus_name: str
    gateway_id: int
    tester_id: int
    ecu_id: int
    def __init__(self, bus_name: _Optional[str] = ..., gateway_id: _Optional[int] = ..., tester_id: _Optional[int] = ..., ecu_id: _Optional[int] = ...) -> None: ...
