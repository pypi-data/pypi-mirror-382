from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESULT_UNDEFINED: _ClassVar[Result]
    RESULT_SUCCESS: _ClassVar[Result]
    RESULT_INVALID_PRECONDITIONS: _ClassVar[Result]
    RESULT_NEEDS_VALIDATION: _ClassVar[Result]
    RESULT_NEEDS_COMPLETION: _ClassVar[Result]
    RESULT_FAILURE_AUTHENTICATION_ERROR: _ClassVar[Result]
    RESULT_FAILURE_MISSING_CODING_INFORMATION: _ClassVar[Result]
    RESULT_FAILURE_NOT_COMPATIBLE: _ClassVar[Result]
    RESULT_FAILURE_COMMUNICATION_ERROR: _ClassVar[Result]
    RESULT_FAILURE_RUNTIME_ERROR: _ClassVar[Result]
    RESULT_FAILURE_EXTERNAL_SERVICE_ERROR: _ClassVar[Result]
    RESULT_FAILURE: _ClassVar[Result]

class UserFeedback(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USER_FEEDBACK_NOTHING: _ClassVar[UserFeedback]
    USER_FEEDBACK_SUCCESS: _ClassVar[UserFeedback]
    USER_FEEDBACK_FAILURE: _ClassVar[UserFeedback]
    USER_FEEDBACK_ASSISTANCE_REQUESTED: _ClassVar[UserFeedback]
RESULT_UNDEFINED: Result
RESULT_SUCCESS: Result
RESULT_INVALID_PRECONDITIONS: Result
RESULT_NEEDS_VALIDATION: Result
RESULT_NEEDS_COMPLETION: Result
RESULT_FAILURE_AUTHENTICATION_ERROR: Result
RESULT_FAILURE_MISSING_CODING_INFORMATION: Result
RESULT_FAILURE_NOT_COMPATIBLE: Result
RESULT_FAILURE_COMMUNICATION_ERROR: Result
RESULT_FAILURE_RUNTIME_ERROR: Result
RESULT_FAILURE_EXTERNAL_SERVICE_ERROR: Result
RESULT_FAILURE: Result
USER_FEEDBACK_NOTHING: UserFeedback
USER_FEEDBACK_SUCCESS: UserFeedback
USER_FEEDBACK_FAILURE: UserFeedback
USER_FEEDBACK_ASSISTANCE_REQUESTED: UserFeedback

class ServiceResult(_message.Message):
    __slots__ = ("result", "user_feedback", "description")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    USER_FEEDBACK_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    result: _containers.RepeatedScalarFieldContainer[Result]
    user_feedback: UserFeedback
    description: str
    def __init__(self, result: _Optional[_Iterable[_Union[Result, str]]] = ..., user_feedback: _Optional[_Union[UserFeedback, str]] = ..., description: _Optional[str] = ...) -> None: ...
