from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CanProtocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAN_PROTOCOL_UNDEFINED: _ClassVar[CanProtocol]
    CAN_PROTOCOL_ISOTP: _ClassVar[CanProtocol]
    CAN_PROTOCOL_TP20: _ClassVar[CanProtocol]
    CAN_PROTOCOL_FRAMES: _ClassVar[CanProtocol]

class CanBitRate(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAN_BIT_RATE_UNDEFINED: _ClassVar[CanBitRate]
    CAN_BIT_RATE_1000: _ClassVar[CanBitRate]
    CAN_BIT_RATE_500: _ClassVar[CanBitRate]
    CAN_BIT_RATE_250: _ClassVar[CanBitRate]
    CAN_BIT_RATE_125: _ClassVar[CanBitRate]
    CAN_BIT_RATE_100: _ClassVar[CanBitRate]
    CAN_BIT_RATE_94: _ClassVar[CanBitRate]
    CAN_BIT_RATE_83_3: _ClassVar[CanBitRate]
    CAN_BIT_RATE_50: _ClassVar[CanBitRate]
    CAN_BIT_RATE_33_3: _ClassVar[CanBitRate]
    CAN_BIT_RATE_20: _ClassVar[CanBitRate]
    CAN_BIT_RATE_10: _ClassVar[CanBitRate]
    CAN_BIT_RATE_5: _ClassVar[CanBitRate]

class TransceiverSpeed(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSCEIVER_SPEED_LOW: _ClassVar[TransceiverSpeed]
    TRANSCEIVER_SPEED_HIGH: _ClassVar[TransceiverSpeed]
CAN_PROTOCOL_UNDEFINED: CanProtocol
CAN_PROTOCOL_ISOTP: CanProtocol
CAN_PROTOCOL_TP20: CanProtocol
CAN_PROTOCOL_FRAMES: CanProtocol
CAN_BIT_RATE_UNDEFINED: CanBitRate
CAN_BIT_RATE_1000: CanBitRate
CAN_BIT_RATE_500: CanBitRate
CAN_BIT_RATE_250: CanBitRate
CAN_BIT_RATE_125: CanBitRate
CAN_BIT_RATE_100: CanBitRate
CAN_BIT_RATE_94: CanBitRate
CAN_BIT_RATE_83_3: CanBitRate
CAN_BIT_RATE_50: CanBitRate
CAN_BIT_RATE_33_3: CanBitRate
CAN_BIT_RATE_20: CanBitRate
CAN_BIT_RATE_10: CanBitRate
CAN_BIT_RATE_5: CanBitRate
TRANSCEIVER_SPEED_LOW: TransceiverSpeed
TRANSCEIVER_SPEED_HIGH: TransceiverSpeed

class CanBus(_message.Message):
    __slots__ = ("pin_plus", "pin_min", "can_protocol", "can_bit_rate", "transceiver")
    PIN_PLUS_FIELD_NUMBER: _ClassVar[int]
    PIN_MIN_FIELD_NUMBER: _ClassVar[int]
    CAN_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    CAN_BIT_RATE_FIELD_NUMBER: _ClassVar[int]
    TRANSCEIVER_FIELD_NUMBER: _ClassVar[int]
    pin_plus: int
    pin_min: int
    can_protocol: CanProtocol
    can_bit_rate: CanBitRate
    transceiver: TransceiverSpeed
    def __init__(self, pin_plus: _Optional[int] = ..., pin_min: _Optional[int] = ..., can_protocol: _Optional[_Union[CanProtocol, str]] = ..., can_bit_rate: _Optional[_Union[CanBitRate, str]] = ..., transceiver: _Optional[_Union[TransceiverSpeed, str]] = ...) -> None: ...
