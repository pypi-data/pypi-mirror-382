import functools
import logging
from collections.abc import Hashable
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING, Any, TypeVar

import httpx

from toolkit import utils
from toolkit.exceptions import ServerError
from toolkit.exceptions import registry as default_registry
from toolkit.exceptions.registry import ExceptionNotFound, ServiceExceptionRegistry
from toolkit.utils import Params, ReturnT

if TYPE_CHECKING:
    from .auth import Auth

logger = logging.getLogger(__name__)

CachedArgT = TypeVar("CachedArgT", bound=Hashable)
CachedReturnT = TypeVar("CachedReturnT")


class ServiceClient(object):
    url: str
    auth: "Auth | None"
    http_client: httpx.Client
    exception_registry: ServiceExceptionRegistry

    def __init__(
        self,
        url: str,
        auth: "Auth | None" = None,
        timeout: int = 10,
        cache_ttl: int = 60 * 15,
    ) -> None:
        self.url = url
        self.auth = auth
        self.ttl_cache = utils.ttl_cache(cache_ttl)
        self.make_http_client(url, auth, timeout)

        if getattr(self, "exception_registry", None) is None:
            self.exception_registry = default_registry

    def make_http_client(self, url: str, auth: "Auth | None", timeout: int) -> None:
        logger.debug(f"Making new http service client for url={url} auth={auth}.")

        self.http_client = httpx.Client(
            base_url=self.url,
            timeout=timeout,
            http2=True,
            auth=auth,
            # We need to set this because the ICT proxy setup
            # does not set some headers properly, resulting in
            # django returning http urls instead of https urls
            # even if configured correctly.
            follow_redirects=True,
        )

    def raise_code_or_unknown(self, message: str | None, res: httpx.Response) -> None:
        try:
            raise self.exception_registry.exception_from_status_code(
                res.status_code, message
            )
        except ExceptionNotFound:
            raise ServerError(message, http_status_code=res.status_code)

    def raise_dict_or_unknown(self, dict_: dict[str, Any], res: httpx.Response) -> None:
        try:
            raise self.exception_registry.exception_from_response_dict(dict_)
        except (ExceptionNotFound, ValueError):
            self.raise_code_or_unknown(dict_.get("name"), res)

    def raise_service_exception(self, res: httpx.Response) -> None:
        if res.is_error:
            try:
                json = res.json()
            except (ValueError, JSONDecodeError):
                self.raise_code_or_unknown(res.text, res)

            self.raise_dict_or_unknown(json, res)

    def jti_cache(
        self, func: utils.CachableCallable[Params, ReturnT]
    ) -> utils.CachableCallable[Params, ReturnT]:
        """Caches a functions results for each unique jwt id using `utils.ttl_cache`"""

        @self.ttl_cache
        @functools.wraps(func)
        def jti_func(
            *args: Params.args, jti: str | None = None, **kwargs: Params.kwargs
        ) -> ReturnT:
            del jti
            return func(*args, **kwargs)

        @functools.wraps(func)
        def wrapper(*args: Hashable, **kwargs: Hashable) -> ReturnT:
            jti = None
            if self.auth is not None:
                if self.auth.access_token is not None:
                    jti = self.auth.access_token.jti
            return jti_func(*args, jti=jti, **kwargs)

        return wrapper
