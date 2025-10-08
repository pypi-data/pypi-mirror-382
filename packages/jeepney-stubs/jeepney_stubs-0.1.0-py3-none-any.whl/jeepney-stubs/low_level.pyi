from _typeshed import FileDescriptorLike, ReadableBuffer
from collections.abc import Iterator, Sequence
from enum import Enum, IntEnum, IntFlag
from typing import Any, Generic, Literal, type_check_only
from typing_extensions import NoReturn, Protocol, TypeVar

_T = TypeVar("_T")
_TPy = TypeVar("_TPy")
_TKey = TypeVar("_TKey")
_TValue = TypeVar("_TValue")

_Signature = str
_DBusObject = tuple[str, _T]

_ParseResult = tuple[_T, int]

endian_map: dict[bytes, Endianness]
header_field_codes: dict[int, str]
simple_types: dict[str, FixedType[object]]

@type_check_only
class Serializable(Protocol[_T]):
    def parse_data(
        self,
        buf: ReadableBuffer,
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptorLike] = (),
    ) -> _ParseResult[_T]: ...
    def serialise(
        self,
        data: _T,
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptorLike] | None = None,
    ) -> bytes: ...

class SizeLimitError(ValueError):
    """Raised when trying to (de-)serialise data exceeding D-Bus' size limit.

    This is currently only implemented for arrays, where the maximum size is
    64 MiB.
    """

    pass

class Endianness(Enum):
    little = 1
    big = 2

    def struct_code(self) -> str: ...
    def dbus_code(self) -> bytes: ...

class MessageType(Enum):
    method_call = 1
    method_return = 2
    error = 3
    signal = 4

class MessageFlag(IntFlag):
    no_reply_expected = 1
    no_auto_start = 2
    allow_interactive_authorization = 4

class HeaderFields(IntEnum):
    path = 1
    interface = 2
    member = 3
    error_name = 4
    reply_serial = 5
    destination = 6
    sender = 7
    signature = 8
    unix_fds = 9

def padding(pos: int, step: int) -> int: ...

class FixedType(Serializable[_T]):
    def __init__(self, size: int, struct_code: str) -> None: ...

class Boolean(FixedType[bool]):
    def __init__(self) -> None: ...

class FileDescriptor(FixedType[FileDescriptorLike]):
    def __init__(self) -> None: ...

class StringType(FixedType[str]):
    def __init__(self, length_type: FixedType[object]) -> None: ...
    @property
    def alignment(self) -> int: ...

    # Can't _exclude_ types with overloads but this throws on non-str data
    def check_data(self, data: object) -> None | NoReturn: ...

class ObjectPathType(StringType):
    def __init__(self) -> None: ...

class Struct:
    alignment: int = 8

    def __init__(
        self,
        fields: list[Array[object] | StringType | FixedType[object] | Variant],
    ) -> None: ...
    def parse_data(
        self,
        buf: bytes,
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptorLike] = ...,
    ) -> _ParseResult[Any]: ...
    def serialise(
        self,
        data: tuple[object, ...],
        pos: int,
        endianness: Endianness,
        fds: None = ...,
    ) -> bytes: ...

class DictEntry(Struct, Generic[_TKey, _TValue]):
    def __init__(self, fields: tuple[_TKey, _TValue]) -> None: ...

_TArrayKey = TypeVar("_TArrayKey", default=object)

# Can't really do proper specialization here but
# array is either an array of a serializable type
# OR a dict of serializable types. the first type
# must be either of fixed size or a string though.
class Array(Generic[_T, _TArrayKey]):
    alignment: int = 4
    length_type: FixedType[int]

    def __init__(
        self, elt_type: Serializable[_T] | DictEntry[_TArrayKey, _T]
    ) -> None: ...
    def parse_data(
        self,
        buf: ReadableBuffer,
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptor] = ...,
    ) -> _ParseResult[list[_T] | dict[_TArrayKey, _T]]: ...
    def serialise(
        self,
        data: bytes | dict[_TArrayKey, _T] | list[_T],
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptorLike] | None = ...,
    ) -> bytes: ...

class Variant:
    alignment: int = 1

    def parse_data(
        self,
        buf: bytes,
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptorLike] = ...,
    ) -> _ParseResult[tuple[_Signature, object]]: ...
    def serialise(
        self,
        data: tuple[_Signature, object],
        pos: int,
        endianness: Endianness,
        fds: None = ...,
    ) -> bytes: ...

def calc_msg_size(buf: bytes) -> int: ...
def parse_header_fields(
    buf: bytes,
    endianness: Endianness,
) -> (
    tuple[dict[HeaderFields, Any], int] 
): ...
def parse_signature(
    sig: list[str],
) -> Struct | Array[object] | StringType | ObjectPathType | FixedType[object]: ...
def serialise_header_fields(
    d: dict[HeaderFields, Any],
    endianness: Endianness,
) -> bytes: ...

class BufferPipe:
    def __init__(self) -> None: ...
    def _peek_iter(self, nbytes: int) -> Iterator[bytes]: ...
    def _read_iter(self, nbytes: int) -> Iterator[bytes]: ...
    def peek(self, nbytes: int) -> bytes: ...
    def read(self, nbytes: int) -> bytes: ...
    def write(self, b: bytes) -> None: ...

class Header:
    endianness: Endianness
    message_type: MessageType
    flags: MessageFlag
    protocol_version: Literal[1]
    body_length: int
    serial: int | None
    fields: dict[HeaderFields, Any]

    def __init__(
        self,
        endianness: Endianness,
        message_type: int | MessageType,
        flags: int,
        protocol_version: int,
        body_length: int,
        serial: int,
        fields: dict[HeaderFields, Any],
    ) -> None: ...
    @classmethod
    def from_buffer(cls, buf: bytes) -> tuple[Header, int]: ...
    def serialise(self, serial: int | None = ...) -> bytes: ...

class Message:
    header: Header
    body: tuple[Any, ...]

    def __init__(self, header: Header, body: tuple[object, ...]) -> None: ...
    @classmethod
    def from_buffer(
        cls, buf: bytes, fds: Sequence[FileDescriptorLike] = ()
    ) -> Message: ...
    def serialise(self, serial: int | None = ..., fds: None = ...) -> bytes: ...

class Parser:
    def __init__(self) -> None: ...
    def add_data(
        self, data: bytes, fds: Sequence[FileDescriptorLike] = ...
    ) -> None: ...
    def get_next_message(self) -> Message | None: ...
    def bytes_desired(self) -> int: ...
    def feed(self, data: bytes) -> list[Message]: ...
