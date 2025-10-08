from _typeshed import Incomplete
import asyncio
from collections.abc import Iterable
from typing import Any, Literal

from ..bus_messages import MatchRule
from ..wrappers import ProxyBase

from ..low_level import Message
from .common import FilterHandle

async def open_dbus_connection(
    bus: str = "SESSION",
) -> DBusConnection: ...

class DBusConnection:
    def __init__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None: ...
    async def send(
        self, message: Message, *, serial: Iterable[int] | None = None
    ) -> None: ...
    async def receive(self) -> Message: ...
    async def close(self) -> None: ...
    async def __aenter__(self) -> DBusConnection: ...
    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> None: ...

class DBusRouter:
    def __init__(self, conn: DBusConnection) -> None: ...
    @property
    def unique_name(self) -> None | Incomplete: ...
    async def send(
        self, message: Message, *, serial: Iterable[int] | None = None
    ) -> None: ...
    async def send_and_get_reply(self, message: Message) -> Message: ...
    async def filter(
        self,
        rule: MatchRule,
        *,
        queue: asyncio.Queue[Message] | None = None,
        bufsize: int = 1,
    ) -> FilterHandle: ...
    async def __aenter__(self) -> DBusRouter: ...
    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> Literal[False]: ...

class open_dbus_router:
    bus: str
    req_ctx: DBusRouter | None
    conn: DBusConnection | None

    def __init__(self, bus: str = "SESSION") -> None: ...
    async def __aenter__(self) -> DBusRouter: ...
    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> None: ...

class Proxy(ProxyBase):
    def __init__(
        self,
        msggen: Any,  # pyright: ignore[reportAny]
        router: DBusRouter,
    ) -> None: ...
