from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class KlineMessage(_message.Message):
    __slots__ = ("channel", "payload")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    channel: KlineChannel
    payload: str
    def __init__(self, channel: _Optional[_Union[KlineChannel, _Mapping]] = ..., payload: _Optional[str] = ...) -> None: ...

class Keyword(_message.Message):
    __slots__ = ("key_byte_1", "key_byte_2")
    KEY_BYTE_1_FIELD_NUMBER: _ClassVar[int]
    KEY_BYTE_2_FIELD_NUMBER: _ClassVar[int]
    key_byte_1: int
    key_byte_2: int
    def __init__(self, key_byte_1: _Optional[int] = ..., key_byte_2: _Optional[int] = ...) -> None: ...

class KlineChannel(_message.Message):
    __slots__ = ("bus_name", "ecu_id", "keyword")
    BUS_NAME_FIELD_NUMBER: _ClassVar[int]
    ECU_ID_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_FIELD_NUMBER: _ClassVar[int]
    bus_name: str
    ecu_id: int
    keyword: Keyword
    def __init__(self, bus_name: _Optional[str] = ..., ecu_id: _Optional[int] = ..., keyword: _Optional[_Union[Keyword, _Mapping]] = ...) -> None: ...
