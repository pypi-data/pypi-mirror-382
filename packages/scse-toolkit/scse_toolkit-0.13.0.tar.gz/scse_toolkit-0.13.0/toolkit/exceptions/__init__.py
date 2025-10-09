"""
The exceptions module for scse services includes:
 - :class:`~toolkit.exceptions.BaseException`: a class that serves as the base class
    for all exceptions in the library.
 - :class:`~toolkit.exceptions.ServiceException`: for serializable exceptions
    that can be raised by a service and parsed by a client.
 - :class:`~toolkit.exceptions.ServiceExceptionRegistry`: a registry for
    :class:`~toolkit.exceptions.ServiceException` classes
"""

from .base import BaseException as BaseException
from .base import ProgrammingError as ProgrammingError
from .registry import ServiceExceptionRegistry
from .serviceexception import ServiceException as ServiceException

registry = ServiceExceptionRegistry()

registry.register()(ServiceException)


@registry.register(default_for_status_code=500)
class ServerError(ServiceException):
    message = "An unknown server error occurred."
    http_status_code = 500


@registry.register(default_for_status_code=502)
class BadGateway(ServiceException):
    message = "Bad Gateway"
    http_status_code = 502


@registry.register(default_for_status_code=503)
class ServiceUnavailable(ServiceException):
    message = "Service Unavailable"
    http_status_code = 503


@registry.register(default_for_status_code=400)
class BadRequest(ServiceException):
    message = "Bad Request"
    http_status_code = 400


@registry.register(default_for_status_code=401)
class Unauthorized(ServiceException):
    message = "Unauthorized"
    http_status_code = 401
    http_error_name = "unauthorized"


@registry.register(default_for_status_code=403)
class Forbidden(ServiceException):
    message = "Authentication credentials indicate insufficient permissions."
    http_status_code = 403


@registry.register(default_for_status_code=404)
class NotFound(ServiceException):
    message = "Not found."
    http_status_code = 404


@registry.register()
class InvalidToken(Unauthorized):
    message = "The supplied token is invalid."
    http_status_code = 401


@registry.register()
class InvalidCredentials(Unauthorized):
    message = "Authentication credentials rejected."
    http_status_code = 401


@registry.register()
class MinioBucketNotFound(ServiceException):
    message = "Minio bucket not found or access denied"
    http_status_code = 404


@registry.register()
class MinioObjectNotFound(ServiceException):
    message = "Minio object not found or access denied"
    http_status_code = 404


@registry.register()
class PlatformNotFound(NotFound):
    message = "Platform not found."
    http_status_code = 404
