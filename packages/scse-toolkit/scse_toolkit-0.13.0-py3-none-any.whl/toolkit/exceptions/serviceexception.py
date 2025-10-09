from typing import Any, Mapping

from .base import BaseException

ExcMeta: type = type(Exception)

DataItemType = (
    None | int | str | bool | list["DataItemType"] | dict[str, "DataItemType"]
)


class ServiceException(BaseException):
    """Base class for serializable exceptions.
    Subclasses can override the :func:`to_dict` and :func:`from_dict` methods to change the
    serialization format, but should ensure it continues to work in a compatible way."""

    http_status_code: int = 500

    data: dict[str, DataItemType]

    def __init__(
        self,
        message: str | None = None,
        http_status_code: int | None = None,
        **data: DataItemType,
    ) -> None:
        """Construction of a new service exception. All arguments except
        `message` and `http_status_code` are stored in the `data` dict."""
        self.message = message or self.message
        self.http_status_code = http_status_code or self.http_status_code

        self.data = data

    @classmethod
    def from_dict(cls, dict_: Mapping[str, Any]) -> "ServiceException":
        message = dict_.get("message", None)
        http_status_code = dict_.get("http_status_code", None)
        return cls(
            message=message,
            http_status_code=http_status_code,
            **dict_.get("data", dict()),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "http_status_code": self.http_status_code,
            "data": self.data,
        }
