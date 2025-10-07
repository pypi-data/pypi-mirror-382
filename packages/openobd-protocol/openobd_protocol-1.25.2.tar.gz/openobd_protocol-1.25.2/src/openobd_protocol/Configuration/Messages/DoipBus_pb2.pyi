from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DoipOption(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DOIP_OPTION_UNDEFINED: _ClassVar[DoipOption]
    DOIP_OPTION_1: _ClassVar[DoipOption]
    DOIP_OPTION_2: _ClassVar[DoipOption]

class DoipNetworkConfiguration(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DOIP_NETWORK_CONFIGURATION_UNDEFINED: _ClassVar[DoipNetworkConfiguration]
    DOIP_NETWORK_CONFIGURATION_1: _ClassVar[DoipNetworkConfiguration]
    DOIP_NETWORK_CONFIGURATION_2: _ClassVar[DoipNetworkConfiguration]
    DOIP_NETWORK_CONFIGURATION_3: _ClassVar[DoipNetworkConfiguration]
    DOIP_NETWORK_CONFIGURATION_4: _ClassVar[DoipNetworkConfiguration]
    DOIP_NETWORK_CONFIGURATION_5: _ClassVar[DoipNetworkConfiguration]
    DOIP_NETWORK_CONFIGURATION_6: _ClassVar[DoipNetworkConfiguration]
    DOIP_NETWORK_CONFIGURATION_7: _ClassVar[DoipNetworkConfiguration]
    DOIP_NETWORK_CONFIGURATION_8: _ClassVar[DoipNetworkConfiguration]
    DOIP_NETWORK_CONFIGURATION_9: _ClassVar[DoipNetworkConfiguration]
DOIP_OPTION_UNDEFINED: DoipOption
DOIP_OPTION_1: DoipOption
DOIP_OPTION_2: DoipOption
DOIP_NETWORK_CONFIGURATION_UNDEFINED: DoipNetworkConfiguration
DOIP_NETWORK_CONFIGURATION_1: DoipNetworkConfiguration
DOIP_NETWORK_CONFIGURATION_2: DoipNetworkConfiguration
DOIP_NETWORK_CONFIGURATION_3: DoipNetworkConfiguration
DOIP_NETWORK_CONFIGURATION_4: DoipNetworkConfiguration
DOIP_NETWORK_CONFIGURATION_5: DoipNetworkConfiguration
DOIP_NETWORK_CONFIGURATION_6: DoipNetworkConfiguration
DOIP_NETWORK_CONFIGURATION_7: DoipNetworkConfiguration
DOIP_NETWORK_CONFIGURATION_8: DoipNetworkConfiguration
DOIP_NETWORK_CONFIGURATION_9: DoipNetworkConfiguration

class DoipBus(_message.Message):
    __slots__ = ("doip_option", "doip_network_configuration")
    DOIP_OPTION_FIELD_NUMBER: _ClassVar[int]
    DOIP_NETWORK_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    doip_option: DoipOption
    doip_network_configuration: DoipNetworkConfiguration
    def __init__(self, doip_option: _Optional[_Union[DoipOption, str]] = ..., doip_network_configuration: _Optional[_Union[DoipNetworkConfiguration, str]] = ...) -> None: ...
