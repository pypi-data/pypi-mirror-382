"""Custom exception hierarchy for the Ca.R.G.O.S. client and mapper."""

class CargoException(Exception):
    """Base exception for all Ca.R.G.O.S.-related errors.

    Use this as a catch-all for library-specific failures.
    """


class InvalidResponse(CargoException):
    """Raised when the remote API returns an error payload or invalid data."""


class InvalidInput(CargoException):
    """Raised when input data is missing, malformed, or inconsistent."""

