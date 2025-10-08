from asyncio import Future
from collections import deque
from typing import Iterable, Literal, NoReturn
from ..low_level import Message
from ..bus_messages import MatchRule
from contextlib import AbstractContextManager

class MessageFilters:
    filters: dict[int, FilterHandle]
    filter_ids: Iterable[int]

    def matches(self, message: Message) -> Iterable[FilterHandle]: ...

class FilterHandle:
    def __init__(
        self, filters: MessageFilters, rule: MatchRule, queue: deque[Message]
    ) -> None: ...
    def close(self) -> None: ...
    def __enter__(self) -> deque[Message]: ...
    def __exit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> Literal[False]: ...

class ReplyMatcher:
    def dispatch(self, msg: Message) -> bool: ...
    def drop_all(self, exc: Exception | None = None) -> None: ...
    def catch(
        self, serial: int, future: Future[Message]
    ) -> AbstractContextManager[Future[Message]]: ...

class RouterClosed(Exception):
    """Raised in tasks waiting for a reply when the router is closed

    This will also be raised if the receiver task crashes, so tasks are not
    stuck waiting for a reply that can never come. The router object will not
    be usable after this is raised.
    """

    ...

def check_replyable(msg: Message) -> None | NoReturn: ...
