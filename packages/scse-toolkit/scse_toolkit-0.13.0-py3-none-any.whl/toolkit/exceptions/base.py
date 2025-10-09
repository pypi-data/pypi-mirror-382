class BaseException(Exception):
    """Base class for all exceptions in the library."""

    message: str | None = None

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message

    def __str__(self) -> str | None:
        return self.message


class ProgrammingError(BaseException):
    """Raised if an error occurs due to the incorrect use of library components."""
