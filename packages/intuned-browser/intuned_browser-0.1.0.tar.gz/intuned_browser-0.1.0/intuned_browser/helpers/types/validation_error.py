from typing import Any


class ValidationError(Exception):
    """Custom validation error with readable message."""

    def __init__(self, message: str, data: Any) -> None:
        self.data = data
        super().__init__(message)
