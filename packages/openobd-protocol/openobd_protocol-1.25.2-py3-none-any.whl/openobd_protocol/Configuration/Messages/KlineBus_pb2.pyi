from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class KlineProtocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KLINE_PROTOCOL_UNDEFINED: _ClassVar[KlineProtocol]
    KLINE_PROTOCOL_ISO14230_SLOW: _ClassVar[KlineProtocol]
    KLINE_PROTOCOL_ISO14230_FAST: _ClassVar[KlineProtocol]

class KlineBitRate(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KLINE_BIT_RATE_UNDEFINED: _ClassVar[KlineBitRate]
    KLINE_BIT_RATE_9600: _ClassVar[KlineBitRate]
    KLINE_BIT_RATE_10400: _ClassVar[KlineBitRate]
    KLINE_BIT_RATE_15625: _ClassVar[KlineBitRate]
KLINE_PROTOCOL_UNDEFINED: KlineProtocol
KLINE_PROTOCOL_ISO14230_SLOW: KlineProtocol
KLINE_PROTOCOL_ISO14230_FAST: KlineProtocol
KLINE_BIT_RATE_UNDEFINED: KlineBitRate
KLINE_BIT_RATE_9600: KlineBitRate
KLINE_BIT_RATE_10400: KlineBitRate
KLINE_BIT_RATE_15625: KlineBitRate

class KlineBus(_message.Message):
    __slots__ = ("pin", "kline_protocol", "kline_bit_rate")
    PIN_FIELD_NUMBER: _ClassVar[int]
    KLINE_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    KLINE_BIT_RATE_FIELD_NUMBER: _ClassVar[int]
    pin: int
    kline_protocol: KlineProtocol
    kline_bit_rate: KlineBitRate
    def __init__(self, pin: _Optional[int] = ..., kline_protocol: _Optional[_Union[KlineProtocol, str]] = ..., kline_bit_rate: _Optional[_Union[KlineBitRate, str]] = ...) -> None: ...
