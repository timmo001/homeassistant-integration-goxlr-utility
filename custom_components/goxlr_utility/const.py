"""Constants for the GoXLR Utility integration."""
from typing import Final

from goxlrutilityapi.exceptions import (
    ConnectionClosedException,
    ConnectionErrorException,
)

DOMAIN: Final[str] = "goxlr_utility"

CONNECTION_ERRORS: Final = (
    ConnectionClosedException,
    ConnectionErrorException,
    ConnectionResetError,
)
