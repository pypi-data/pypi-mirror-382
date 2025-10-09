from google.api import annotations_pb2 as _annotations_pb2
from nominal.gen.v1 import error_pb2 as _error_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Platform(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLATFORM_UNSPECIFIED: _ClassVar[Platform]
    PLATFORM_MACOS: _ClassVar[Platform]
    PLATFORM_WINDOWS: _ClassVar[Platform]
    PLATFORM_UBUNTU: _ClassVar[Platform]

class ConnectDownloadServiceError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONNECT_DOWNLOAD_SERVICE_ERROR_UNSPECIFIED: _ClassVar[ConnectDownloadServiceError]
    CONNECT_DOWNLOAD_SERVICE_ERROR_CONNECT_NOT_AVAILABLE: _ClassVar[ConnectDownloadServiceError]
PLATFORM_UNSPECIFIED: Platform
PLATFORM_MACOS: Platform
PLATFORM_WINDOWS: Platform
PLATFORM_UBUNTU: Platform
CONNECT_DOWNLOAD_SERVICE_ERROR_UNSPECIFIED: ConnectDownloadServiceError
CONNECT_DOWNLOAD_SERVICE_ERROR_CONNECT_NOT_AVAILABLE: ConnectDownloadServiceError

class GetLatestConnectUriRequest(_message.Message):
    __slots__ = ("platform",)
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    platform: Platform
    def __init__(self, platform: _Optional[_Union[Platform, str]] = ...) -> None: ...

class GetLatestConnectUriResponse(_message.Message):
    __slots__ = ("uri",)
    URI_FIELD_NUMBER: _ClassVar[int]
    uri: str
    def __init__(self, uri: _Optional[str] = ...) -> None: ...
