from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Terminal15State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATE_UNDEFINED: _ClassVar[Terminal15State]
    STATE_ON: _ClassVar[Terminal15State]
    STATE_OFF: _ClassVar[Terminal15State]
STATE_UNDEFINED: Terminal15State
STATE_ON: Terminal15State
STATE_OFF: Terminal15State

class Terminal15Message(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: Terminal15State
    def __init__(self, state: _Optional[_Union[Terminal15State, str]] = ...) -> None: ...
