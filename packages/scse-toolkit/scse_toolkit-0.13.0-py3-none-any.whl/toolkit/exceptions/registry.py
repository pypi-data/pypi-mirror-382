from typing import Any, Callable

from .base import BaseException, ProgrammingError
from .serviceexception import ServiceException


class ExceptionNotFound(BaseException):
    """Exception raised when an exception class is not found in the registry."""

    message = "Exception class not found in registry."


class ServiceExceptionRegistry(object):
    """Registry for :class:`.ServiceException` classes.
    This registry is used to register exception classes that can be raised
    by a service and parsed by a client.
    It is used to map exception classes to status codes and names, and to
    create instances of the exception classes from dictionaries or status
    codes.

    A basic exceptions module would make a new registry and register
    some exceptions:

    .. code :: python
        from toolkit.exceptions import (
            ServiceException,
            ServiceExceptionRegistry,
            registry as default_registry
        )

        registry = ServiceExceptionRegistry()

        # or copy the default registry:

        registry = default_registry.copy()

        @registry.register()
        class CustomException(ServiceException):
            http_status_code = 400

        @registry.register(name="alternative_name")
        class NamedCustomException(ServiceException):
            http_status_code = 400

        @registry.register(default_for_status_code=412)
        class DefaultCustomException(ServiceException):
            http_status_code = 412

    The registry can then be used to serialize exceptions, for example
    in a fastapi exception handler:

    .. code :: python
        from fastapi import FastAPI, Response
        from fastapi.encoders import jsonable_encoder
        from .exceptions import registry, ServiceException

        app = FastAPI()

        @app.exception_handler(ServiceException)
        async def http_exception_handler(request: Request, exc: ServiceException):
            exc_dict = registry.exception_to_response_dict(exc)

            return JSONResponse(
                content=jsonable_encoder(exc_dict),
                status_code=exc.http_status_code,
            )

    And to deserialize exceptions from a response dictionary in a client:

    .. code :: python
        import httpx
        from json.decoder import JSONDecodeError
        from .exceptions import registry

        def raise_service_exception(res: httpx.Response) -> None:
            if res.is_error:
                try:
                    json = res.json()
                except (ValueError, JSONDecodeError):
                    raise registry.exception_from_status_code(
                        res.status_code, message=res.text
                    )

                raise registry.exception_from_response_dict(json)
    """

    items: dict[str, type["ServiceException"]]
    defaults: dict[int, type["ServiceException"]]

    _reverse_items: dict[type["ServiceException"], str]
    _reverse_defaults: dict[type["ServiceException"], int]

    def __init__(
        self,
        items: dict[str, type["ServiceException"]] | None = None,
        defaults: dict[int, type["ServiceException"]] | None = None,
    ) -> None:
        self.items = items or {}
        self.defaults = defaults or {}
        self._reverse_items = {}
        self._reverse_defaults = {}

        for name, class_ in self.items.items():
            self._reverse_items[class_] = name

        for code, class_ in self.defaults.items():
            self._reverse_defaults[class_] = code

    def get_class_for_status_code(
        self, status_code: int
    ) -> type["ServiceException"] | None:
        """Returns the default exception class for the given status code."""
        return self.defaults.get(status_code)

    def get_class_for_name(self, name: str) -> type["ServiceException"] | None:
        """Returns the exception class for the given name."""
        return self.items.get(name)

    def exception_from_status_code(
        self, status_code: int, message: str | None = None
    ) -> "ServiceException":
        """Returns an instance of the default exception class for the given
        status code."""
        exc_class = self.get_class_for_status_code(status_code)

        if exc_class is None:
            raise ExceptionNotFound(
                f"No generic exception available for status code {str(status_code)}."
            )

        return exc_class(message)

    def exception_from_response_dict(self, dict_: dict[str, Any]) -> "ServiceException":
        """Returns an instance of the exception class for the given dictionary.
        The dictionary must contain a `name` key, which is used to look up the
        exception class in the registry."""

        name = dict_.get("name")

        if not isinstance(name, str):
            raise ValueError(
                "`A valid string `name` item is required in the supplied dictionary."
            )

        exc_class = self.get_class_for_name(name)

        if exc_class is None:
            raise ExceptionNotFound(
                f"Exception class for name '{name}' not found in registry."
            )

        return exc_class.from_dict(dict_)

    def exception_to_response_dict(
        self, exc: "ServiceException | type[ServiceException]"
    ) -> dict[str, Any]:
        """Returns a dictionary representation of the given exception.
        The dictionary will contain the `name`, `args`, and `kwargs` of the
        exception."""
        name = None
        if isinstance(exc, ServiceException):
            name = self._reverse_items.get(exc.__class__)
        elif issubclass(exc, ServiceException):
            name = self._reverse_items.get(exc)
            exc = exc()

        if name is None:
            raise ExceptionNotFound(
                f"The exception `{exc.__class__}` is not registered in this registry."
            )

        return {
            **exc.to_dict(),
            "name": name,
        }

    def copy(self) -> "ServiceExceptionRegistry":
        """Returns an independent copy of the registry."""
        return ServiceExceptionRegistry(
            items=self.items.copy(),
            defaults=self.defaults.copy(),
        )

    def register(
        self,
        name: str | None = None,
        default_for_status_code: int | None = None,
    ) -> Callable[[type["ServiceException"]], type["ServiceException"]]:
        """Decorator to register a new exception class in the registry.
        If `default_for_status_code` is set, the exception will be registered
        as a default exception for the given status code.

        Parameters
        ----------
        name: str | None
            The name of the exception class to register. If `None`, the name
            will be derived from the class name.
        default_for_status_code: int | None
            The status code to register the exception class for. If `None`,
            the exception class will not be registered as a default exception.

        Raises
        ------
        ProgrammingError: If the exception class is not a subclass of `Service
            Exception`, or if the name or status code is already registered."""

        def decorator(
            exc_class: type["ServiceException"], name: str | None = name
        ) -> type["ServiceException"]:
            if not issubclass(exc_class, ServiceException):
                raise ProgrammingError(
                    "Only subclasses of `ServiceException` can be registered."
                )

            if name is None:
                name = exc_class.__name__

            if name in self.items:
                duplicate = self.items[name]
                raise ProgrammingError(
                    "Duplicate exception name in registry: "
                    f"{duplicate.__module__}.{duplicate.__name__} "
                    f"is already registered as '{name}'."
                )
            else:
                self.items[name] = exc_class
                self._reverse_items[exc_class] = name

            if default_for_status_code is not None:
                if default_for_status_code in self.defaults:
                    duplicate = self.defaults[default_for_status_code]
                    raise ProgrammingError(
                        "Duplicate status code in default exception registry: "
                        f"{duplicate.__module__}.{duplicate.__name__} is already "
                        f"registered as a default for status '{default_for_status_code}'."
                    )
                else:
                    self.defaults[default_for_status_code] = exc_class
                    self._reverse_defaults[exc_class] = default_for_status_code

            return exc_class

        return decorator
