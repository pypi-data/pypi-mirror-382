from collections import deque
from collections.abc import Iterable
from socket import socket
from typing import Any, Literal

from ..bus_messages import MatchRule
from ..wrappers import ProxyBase

from ..low_level import Message
from .common import FilterHandle

__all__ = [
    "open_dbus_connection",
    "DBusConnection",
    "Proxy",
]

def open_dbus_connection(
    bus: str = "SESSION",
    enable_fds: bool = False,
    auth_timeout: float = 1.0,
) -> DBusConnection: ...

class DBusConnectionBase:
    def __init__(self, sock: socket, enable_fds: bool = False) -> None: ...
    def __enter__(self) -> DBusConnection: ...
    def __exit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> Literal[False]: ...
    def close(self) -> None: ...

class DBusConnection(DBusConnectionBase):
    def send(self, message: Message, serial: Iterable[int] | None = None) -> None: ...

    # for backwards compat reasons, note that the actual lib just assigns it to send
    def send_message(
        self, message: Message, serial: Iterable[int] | None = None
    ) -> None: ...
    def receive(self, *, timeout: float | None = None) -> Message: ...
    def recv_messages(self, *, timeout: float | None = None) -> None: ...
    def send_and_get_reply(
        self, message: Message, *, timeout: float | None = None
    ) -> Message: ...
    def filter(
        self, rule: MatchRule, *, queue: deque[Message] | None = None, bufsize: int = 1
    ) -> FilterHandle: ...
    def recv_until_filtered(
        self, queue: deque[Message], *, timeout: float | None = None
    ) -> Message: ...

class Proxy(ProxyBase):
    def __init__(
        self,
        msggen: Any,  # pyright: ignore[reportAny]
        connection: DBusConnection,
        *,
        timeout: float | None = ...,
    ) -> None: ...
