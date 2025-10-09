"""
Vaultik API Client for Python
Official client library for Vaultik AI Authentication API
"""

from .client import VaultikClient
from .exceptions import (
    VaultikAPIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    JobFailedError
)

__version__ = "1.1.0"
__all__ = [
    "VaultikClient",
    "VaultikAPIError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "JobFailedError"
]
