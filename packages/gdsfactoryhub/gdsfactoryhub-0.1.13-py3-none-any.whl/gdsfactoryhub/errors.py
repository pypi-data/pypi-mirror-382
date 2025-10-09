"""Module for defining custom exceptions for the DoData library."""


class DoDataError(Exception):
    """Base class for all DoData exceptions."""

    def __init__(self, message: str) -> None:
        """Initialize the DoDataError with a custom message."""
        self.message = message
        super().__init__(self.message)
