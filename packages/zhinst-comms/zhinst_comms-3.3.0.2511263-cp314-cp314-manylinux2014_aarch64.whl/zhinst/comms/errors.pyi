"""Exception classes."""

from __future__ import annotations

from zhinst.comms._comms.errors import BadRequestError
from zhinst.comms._comms.errors import BaseError
from zhinst.comms._comms.errors import CancelledError
from zhinst.comms._comms.errors import NotFoundError
from zhinst.comms._comms.errors import OverwhelmedError
from zhinst.comms._comms.errors import TimeoutError
from zhinst.comms._comms.errors import UnavailableError
from zhinst.comms._comms.errors import UnimplementedError
from zhinst.comms._comms.errors import DisconnectError

__all__ = [
    "BadRequestError",
    "BaseError",
    "CancelledError",
    "NotFoundError",
    "OverwhelmedError",
    "TimeoutError",
    "UnavailableError",
    "UnimplementedError",
    "DisconnectError",
]
