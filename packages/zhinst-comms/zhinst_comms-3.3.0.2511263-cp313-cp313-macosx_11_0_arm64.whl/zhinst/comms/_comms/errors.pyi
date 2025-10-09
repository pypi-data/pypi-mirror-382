"""Exception classes."""

from __future__ import annotations

__all__ = [
    "BadRequestError",
    "BaseError",
    "CancelledError",
    "DisconnectError",
    "NotFoundError",
    "OverwhelmedError",
    "TimeoutError",
    "UnavailableError",
    "UnimplementedError",
]

class BadRequestError(Exception):
    pass

class BaseError(Exception):
    pass

class CancelledError(Exception):
    pass

class DisconnectError(Exception):
    pass

class NotFoundError(Exception):
    pass

class OverwhelmedError(Exception):
    pass

class TimeoutError(Exception):
    pass

class UnavailableError(Exception):
    pass

class UnimplementedError(Exception):
    pass
