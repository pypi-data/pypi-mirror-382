"""
Promptware Python Client Library

Provides MCP client for calling Promptware services over HTTP.
"""

from .client import MCPClient, call_verb
from .exceptions import (
    ConnectionError,
    InvalidParamsError,
    InvalidVerbError,
    MCPError,
    ProtocolError,
    ServiceUnavailableError,
    TimeoutError,
)

__version__ = "2.1.0b1"

__all__ = [
    "MCPClient",
    "call_verb",
    "MCPError",
    "ConnectionError",
    "TimeoutError",
    "ServiceUnavailableError",
    "InvalidVerbError",
    "InvalidParamsError",
    "ProtocolError",
]
