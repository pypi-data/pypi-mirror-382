from openobd_protocol.Configuration.Messages import BusConfiguration_pb2 as _BusConfiguration_pb2
from openobd_protocol.Communication.Messages import Raw_pb2 as _Raw_pb2
from openobd_protocol.Communication.Messages import Isotp_pb2 as _Isotp_pb2
from openobd_protocol.Communication.Messages import Kline_pb2 as _Kline_pb2
from openobd_protocol.Communication.Messages import Tp20_pb2 as _Tp20_pb2
from openobd_protocol.Communication.Messages import Doip_pb2 as _Doip_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfiguredChannel(_message.Message):
    __slots__ = ("raw_channel", "isotp_channel", "kline_channel", "tp20_channel", "doip_channel")
    RAW_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    ISOTP_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    KLINE_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    TP20_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    DOIP_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    raw_channel: _Raw_pb2.RawChannel
    isotp_channel: _Isotp_pb2.IsotpChannel
    kline_channel: _Kline_pb2.KlineChannel
    tp20_channel: _Tp20_pb2.Tp20Channel
    doip_channel: _Doip_pb2.DoipChannel
    def __init__(self, raw_channel: _Optional[_Union[_Raw_pb2.RawChannel, _Mapping]] = ..., isotp_channel: _Optional[_Union[_Isotp_pb2.IsotpChannel, _Mapping]] = ..., kline_channel: _Optional[_Union[_Kline_pb2.KlineChannel, _Mapping]] = ..., tp20_channel: _Optional[_Union[_Tp20_pb2.Tp20Channel, _Mapping]] = ..., doip_channel: _Optional[_Union[_Doip_pb2.DoipChannel, _Mapping]] = ...) -> None: ...

class Configuration(_message.Message):
    __slots__ = ("buses", "channels")
    BUSES_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    buses: _containers.RepeatedCompositeFieldContainer[_BusConfiguration_pb2.BusConfiguration]
    channels: _containers.RepeatedCompositeFieldContainer[ConfiguredChannel]
    def __init__(self, buses: _Optional[_Iterable[_Union[_BusConfiguration_pb2.BusConfiguration, _Mapping]]] = ..., channels: _Optional[_Iterable[_Union[ConfiguredChannel, _Mapping]]] = ...) -> None: ...
