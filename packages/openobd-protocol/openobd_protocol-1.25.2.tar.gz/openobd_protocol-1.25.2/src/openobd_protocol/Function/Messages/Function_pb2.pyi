from openobd_protocol.Session.Messages import ServiceResult_pb2 as _ServiceResult_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContextType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNDEFINED_CONTEXT: _ClassVar[ContextType]
    GLOBAL_CONTEXT: _ClassVar[ContextType]
    FUNCTION_CONTEXT: _ClassVar[ContextType]
    CONNECTION_CONTEXT: _ClassVar[ContextType]
UNDEFINED_CONTEXT: ContextType
GLOBAL_CONTEXT: ContextType
FUNCTION_CONTEXT: ContextType
CONNECTION_CONTEXT: ContextType

class FunctionContext(_message.Message):
    __slots__ = ("id", "finished", "monitor_token", "authentication_token", "service_result")
    ID_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    MONITOR_TOKEN_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SERVICE_RESULT_FIELD_NUMBER: _ClassVar[int]
    id: str
    finished: bool
    monitor_token: str
    authentication_token: str
    service_result: _ServiceResult_pb2.ServiceResult
    def __init__(self, id: _Optional[str] = ..., finished: bool = ..., monitor_token: _Optional[str] = ..., authentication_token: _Optional[str] = ..., service_result: _Optional[_Union[_ServiceResult_pb2.ServiceResult, _Mapping]] = ...) -> None: ...

class FunctionId(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class FunctionDetails(_message.Message):
    __slots__ = ("id", "version", "name", "description", "products", "vehicles")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    VEHICLES_FIELD_NUMBER: _ClassVar[int]
    id: str
    version: str
    name: str
    description: str
    products: _containers.RepeatedCompositeFieldContainer[Product]
    vehicles: _containers.RepeatedCompositeFieldContainer[Vehicle]
    def __init__(self, id: _Optional[str] = ..., version: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ..., vehicles: _Optional[_Iterable[_Union[Vehicle, _Mapping]]] = ...) -> None: ...

class Product(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class Vehicle(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class VariableSelection(_message.Message):
    __slots__ = ("type", "prefix")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    type: ContextType
    prefix: str
    def __init__(self, type: _Optional[_Union[ContextType, str]] = ..., prefix: _Optional[str] = ...) -> None: ...

class VariableList(_message.Message):
    __slots__ = ("variables",)
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    variables: _containers.RepeatedCompositeFieldContainer[Variable]
    def __init__(self, variables: _Optional[_Iterable[_Union[Variable, _Mapping]]] = ...) -> None: ...

class Variable(_message.Message):
    __slots__ = ("type", "key", "value", "object")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    type: ContextType
    key: str
    value: str
    object: _any_pb2.Any
    def __init__(self, type: _Optional[_Union[ContextType, str]] = ..., key: _Optional[str] = ..., value: _Optional[str] = ..., object: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
