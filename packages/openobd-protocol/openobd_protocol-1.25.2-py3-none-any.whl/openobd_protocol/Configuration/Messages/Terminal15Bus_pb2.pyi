from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Terminal15Bus(_message.Message):
    __slots__ = ("pin",)
    PIN_FIELD_NUMBER: _ClassVar[int]
    pin: int
    def __init__(self, pin: _Optional[int] = ...) -> None: ...
