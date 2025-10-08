from collections.abc import Callable
from typing import Any
from typing_extensions import Self

from .low_level import Message

__all__ = [
    "DBusAddress",
    "new_method_call",
    "new_method_return",
    "new_error",
    "new_signal",
    "MessageGenerator",
    "Properties",
    "Introspectable",
    "DBusErrorResponse",
]

_Signature = str

class DBusAddress:
    object_path: str
    bus_name: str | None
    interface: str | None

    def __init__(
        self,
        object_path: str,
        bus_name: str | None = ...,
        interface: str | None = ...,
    ) -> None: ...
    def with_interface(self, interface: str) -> Self: ...

def new_method_call(
    remote_obj: DBusAddress | MessageGenerator,
    method: str,
    signature: str | None = ...,
    body: tuple[object, ...] = (),
) -> Message: ...
def new_method_return(
    parent_msg: Message, signature: str | None = None, body: tuple[object, ...] = ()
) -> Message: ...
def new_error(
    parent_msg: Message,
    error_name: str,
    signature: str | None = None,
    body: tuple[object, ...] = (),
) -> Message: ...
def new_signal(
    emitter: DBusAddress,
    signal: str,
    signature: str | None = None,
    body: tuple[object, ...] = (),
) -> Message: ...
def unwrap_msg(msg: Message) -> tuple[list[Any]] | tuple[str]: ...

class MessageGenerator:
    interface: str | None
    def __init__(self, object_path: str, bus_name: str) -> None: ...

# magic / TODO
class ProxyBase:
    def __getattr__(self, item: str) -> Callable[..., object]: ...
    # really msggen is more abstract than this / TODO?
    def __init__(self, msggen: Properties | MessageGenerator) -> None: ...

class Introspectable(MessageGenerator):
    interface: str  # pyright: ignore[reportIncompatibleVariableOverride]
    def Introspect(self) -> Message: ...

class Properties:
    obj: DBusAddress | MessageGenerator
    props_if: DBusAddress

    def __init__(self, obj: DBusAddress | MessageGenerator) -> None: ...
    def get(self, name: str) -> Message: ...
    def get_all(self) -> dict[str, tuple[_Signature, Any]]: ...
    def set(self, name: str, signature: _Signature, value: object) -> Message: ...

class DBusErrorResponse(Exception):
    name: str
    data: tuple[Any, ...]

    def __init__(self, msg: Message) -> None: ...
    ...
