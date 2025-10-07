"""
Exceptions
----------

This only contains one class and that is AresError
"""

class AresError(Exception):
    """Raised when c-ares fails to do something"""

    status: int
    strerror: bytes
    name: bytes
    def __init__(self, status: int) -> None: ...
    def __str__(self) -> str: ...
