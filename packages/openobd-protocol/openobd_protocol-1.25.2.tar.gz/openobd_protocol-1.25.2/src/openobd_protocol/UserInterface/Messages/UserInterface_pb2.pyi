from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InterfaceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INTERFACE_UNDEFINED: _ClassVar[InterfaceType]
    INTERFACE_USER: _ClassVar[InterfaceType]
    INTERFACE_OPERATOR: _ClassVar[InterfaceType]
INTERFACE_UNDEFINED: InterfaceType
INTERFACE_USER: InterfaceType
INTERFACE_OPERATOR: InterfaceType

class Control(_message.Message):
    __slots__ = ("target", "control_label", "control_options", "control_continue", "control_yesno", "control_freetext", "control_number", "translations", "image")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    CONTROL_LABEL_FIELD_NUMBER: _ClassVar[int]
    CONTROL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CONTROL_CONTINUE_FIELD_NUMBER: _ClassVar[int]
    CONTROL_YESNO_FIELD_NUMBER: _ClassVar[int]
    CONTROL_FREETEXT_FIELD_NUMBER: _ClassVar[int]
    CONTROL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONS_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    target: InterfaceType
    control_label: Label
    control_options: Options
    control_continue: Continue
    control_yesno: YesNo
    control_freetext: FreeText
    control_number: Numbers
    translations: _containers.RepeatedCompositeFieldContainer[LabelTranslations]
    image: Image
    def __init__(self, target: _Optional[_Union[InterfaceType, str]] = ..., control_label: _Optional[_Union[Label, _Mapping]] = ..., control_options: _Optional[_Union[Options, _Mapping]] = ..., control_continue: _Optional[_Union[Continue, _Mapping]] = ..., control_yesno: _Optional[_Union[YesNo, _Mapping]] = ..., control_freetext: _Optional[_Union[FreeText, _Mapping]] = ..., control_number: _Optional[_Union[Numbers, _Mapping]] = ..., translations: _Optional[_Iterable[_Union[LabelTranslations, _Mapping]]] = ..., image: _Optional[_Union[Image, _Mapping]] = ...) -> None: ...

class LabelTranslations(_message.Message):
    __slots__ = ("label", "translations")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    TRANSLATIONS_FIELD_NUMBER: _ClassVar[int]
    label: str
    translations: _containers.RepeatedCompositeFieldContainer[Translation]
    def __init__(self, label: _Optional[str] = ..., translations: _Optional[_Iterable[_Union[Translation, _Mapping]]] = ...) -> None: ...

class Translation(_message.Message):
    __slots__ = ("language", "label")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    language: str
    label: str
    def __init__(self, language: _Optional[str] = ..., label: _Optional[str] = ...) -> None: ...

class Label(_message.Message):
    __slots__ = ("label", "minimal_display_time")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    MINIMAL_DISPLAY_TIME_FIELD_NUMBER: _ClassVar[int]
    label: str
    minimal_display_time: int
    def __init__(self, label: _Optional[str] = ..., minimal_display_time: _Optional[int] = ...) -> None: ...

class Options(_message.Message):
    __slots__ = ("label", "options", "answer")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    label: str
    options: _containers.RepeatedScalarFieldContainer[str]
    answer: int
    def __init__(self, label: _Optional[str] = ..., options: _Optional[_Iterable[str]] = ..., answer: _Optional[int] = ...) -> None: ...

class Continue(_message.Message):
    __slots__ = ("label",)
    LABEL_FIELD_NUMBER: _ClassVar[int]
    label: str
    def __init__(self, label: _Optional[str] = ...) -> None: ...

class YesNo(_message.Message):
    __slots__ = ("label", "answer")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    label: str
    answer: bool
    def __init__(self, label: _Optional[str] = ..., answer: bool = ...) -> None: ...

class FreeText(_message.Message):
    __slots__ = ("label", "answer")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    label: str
    answer: str
    def __init__(self, label: _Optional[str] = ..., answer: _Optional[str] = ...) -> None: ...

class Numbers(_message.Message):
    __slots__ = ("label", "minimum", "maximum", "answer")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    label: str
    minimum: int
    maximum: int
    answer: int
    def __init__(self, label: _Optional[str] = ..., minimum: _Optional[int] = ..., maximum: _Optional[int] = ..., answer: _Optional[int] = ...) -> None: ...

class Image(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...
