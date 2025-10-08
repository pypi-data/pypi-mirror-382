from collections.abc import Iterable
from enum import Enum

BEGIN: bytes
NEGOTIATE_UNIX_FD: bytes

def make_auth_external() -> bytes: ...
def make_auth_anonymous() -> bytes: ...

class ClientState(Enum):
    # States from the D-Bus spec (plus 'Success'). Not all used in Jeepney.
    WaitingForData = 1
    WaitingForOk = 2
    WaitingForReject = 3
    WaitingForAgreeUnixFD = 4
    Success = 5

class AuthenticationError(ValueError):
    def __init__(self, data: bytearray, msg: str = ...) -> None: ...

    data: bytearray
    msg: str

class FDNegotiationError(AuthenticationError):
    def __init__(self, data: bytearray) -> None: ...

class Authenticator:
    enable_fds: bool
    buffer: bytearray
    state: ClientState
    error: AuthenticationError

    def __init__(
        self, enable_fds: bool = False, inc_null_byte: bool = True
    ) -> None: ...
    @property
    def authenticated(self) -> bool: ...
    def __iter__(self) -> Iterable[bytes]:
        pass

    def data_to_send(self) -> bytes | None: ...
    def process_line(self, line: bytearray) -> None: ...
    def feed(self, data: bytes) -> None: ...

SASLParser = Authenticator
