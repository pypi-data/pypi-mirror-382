from openobd_protocol.Configuration.Messages import CanBus_pb2 as _CanBus_pb2
from openobd_protocol.Configuration.Messages import KlineBus_pb2 as _KlineBus_pb2
from openobd_protocol.Configuration.Messages import Terminal15Bus_pb2 as _Terminal15Bus_pb2
from openobd_protocol.Configuration.Messages import DoipBus_pb2 as _DoipBus_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BusConfiguration(_message.Message):
    __slots__ = ("bus_name", "can_bus", "kline_bus", "terminal15_bus", "doip_bus")
    BUS_NAME_FIELD_NUMBER: _ClassVar[int]
    CAN_BUS_FIELD_NUMBER: _ClassVar[int]
    KLINE_BUS_FIELD_NUMBER: _ClassVar[int]
    TERMINAL15_BUS_FIELD_NUMBER: _ClassVar[int]
    DOIP_BUS_FIELD_NUMBER: _ClassVar[int]
    bus_name: str
    can_bus: _CanBus_pb2.CanBus
    kline_bus: _KlineBus_pb2.KlineBus
    terminal15_bus: _Terminal15Bus_pb2.Terminal15Bus
    doip_bus: _DoipBus_pb2.DoipBus
    def __init__(self, bus_name: _Optional[str] = ..., can_bus: _Optional[_Union[_CanBus_pb2.CanBus, _Mapping]] = ..., kline_bus: _Optional[_Union[_KlineBus_pb2.KlineBus, _Mapping]] = ..., terminal15_bus: _Optional[_Union[_Terminal15Bus_pb2.Terminal15Bus, _Mapping]] = ..., doip_bus: _Optional[_Union[_DoipBus_pb2.DoipBus, _Mapping]] = ...) -> None: ...
