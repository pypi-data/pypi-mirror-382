from .sandbox_client import InstaVM
from .exceptions import (
    InstaVMError,
    AuthenticationError, 
    SessionError,
    ExecutionError,
    NetworkError,
    RateLimitError,
    BrowserError,
    BrowserSessionError,
    BrowserInteractionError,
    BrowserTimeoutError,
    BrowserNavigationError,
    ElementNotFoundError,
    QuotaExceededError
)

# LLM integrations - optional imports
__all__ = [
    "InstaVM",
    "InstaVMError",
    "AuthenticationError",
    "SessionError", 
    "ExecutionError",
    "NetworkError",
    "RateLimitError",
    "BrowserError",
    "BrowserSessionError",
    "BrowserInteractionError",
    "BrowserTimeoutError",
    "BrowserNavigationError",
    "ElementNotFoundError",
    "QuotaExceededError"
]
