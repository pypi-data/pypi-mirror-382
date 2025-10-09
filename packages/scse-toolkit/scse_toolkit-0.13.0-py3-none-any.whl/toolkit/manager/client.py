import json
import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, Generic, TypedDict, TypeVar, cast

import httpx
import polars as pl
from httpx import QueryParams
from pydantic import BaseModel
from typing_extensions import Unpack

from toolkit import utils
from toolkit.client.base import ServiceClient

from .models import Ixmp4Instance, ModelPermission, Root, User

if TYPE_CHECKING:
    from toolkit.client.auth import Auth

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)

ttl_cache = utils.ttl_cache()


class EnumerateKwargs(TypedDict, total=False):
    page_size: int
    page: int


class DjangoEnumerationResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[dict[str, object]]


class PaginatedResult(BaseModel):
    count: int
    results: list[dict[str, object]]


class BaseRepository(Generic[ModelType]):
    response_model: type[ModelType]
    prefix: str
    client: ServiceClient

    def __init__(
        self, client: ServiceClient, prefix: str, response_model: type[ModelType]
    ) -> None:
        self.client = client
        self.prefix = prefix
        self.response_model = response_model

        if not self.prefix.endswith("/"):
            self.prefix += "/"

        self.cached_list = self.client.jti_cache(self.list)
        self.cached_tabulate = self.client.jti_cache(self.tabulate)
        self.cached_retrieve = self.client.jti_cache(self.retrieve)

    def normalize_params(self, params: EnumerateKwargs) -> QueryParams:
        """Encodes list parameters as comma-seperated strings because
        httpx does not have a way to customize this behaviour."""

        norm_params: QueryParams = QueryParams()
        for key, val in params.items():
            if isinstance(val, Iterable) and not isinstance(val, str):
                list_ = list(json.dumps(i) for i in val)
                norm_params = norm_params.add(key, ",".join(list_))
            else:
                norm_params = norm_params.add(key, val)
        return norm_params

    def enumerate_paginated(self, **kwargs: Unpack[EnumerateKwargs]) -> PaginatedResult:
        initial_repsonse = self.enumerate(**kwargs)
        result = PaginatedResult(
            count=initial_repsonse.count, results=initial_repsonse.results
        )
        next_url = initial_repsonse.next
        while next_url is not None:
            res = self.client.http_client.get(next_url)
            self.client.raise_service_exception(res)
            json = res.json()
            enumeration_response = DjangoEnumerationResponse.model_validate(json)
            next_url = enumeration_response.next
            result.results.extend(enumeration_response.results)
            result.count = enumeration_response.count

        return result

    def enumerate(self, **kwargs: Unpack[EnumerateKwargs]) -> DjangoEnumerationResponse:
        res = self.client.http_client.get(
            self.prefix,
            params=self.normalize_params(kwargs),
        )
        self.client.raise_service_exception(res)
        json = res.json()
        return DjangoEnumerationResponse.model_validate(json)

    def list(self, **kwargs: object) -> list[ModelType]:
        """Retrieves a list of objects."""
        logger.debug(f"Listing `{self.response_model.__name__}` objects...")
        res = self.enumerate_paginated(**cast(EnumerateKwargs, kwargs))
        return [self.response_model(**r) for r in res.results]

    def tabulate(self, **kwargs: object) -> pl.DataFrame:
        """Retrieves a list of objects and puts them in a Dataframe."""
        logger.debug(f"Tabulating `{self.response_model.__name__}` objects...")
        res = self.enumerate_paginated(**cast(EnumerateKwargs, kwargs))
        return pl.DataFrame(res.results)

    def retrieve(self, id: int) -> ModelType:
        """Retrieves an object with the supplied id."""
        logger.debug(f"Retrieving `{self.response_model.__name__}` object...")
        res = self.client.http_client.get(self.prefix + str(id) + "/")
        self.client.raise_service_exception(res)
        return self.response_model(**res.json())


class UserEnumerateKwargs(EnumerateKwargs):
    search: str
    groups__id__in: list[int]


class UserRepository(BaseRepository[User]):
    def __init__(self, client: ServiceClient) -> None:
        super().__init__(client, "users/", User)

    def impersonate(self, id: int) -> dict[str, str]:
        """Retrieves new authentication tokens for the
        user with the supplied id. Only works if
        a `superuser` authentication token is set."""

        res = self.client.http_client.get(self.prefix + str(id) + "/impersonate/")
        self.client.raise_service_exception(res)
        return cast(dict[str, str], res.json())

    def me(self) -> User:
        """Retrieves the current user if an authentication
        token is set."""

        res = self.client.http_client.get(self.prefix + "me/")
        self.client.raise_service_exception(res)
        user: User = self.response_model(**res.json())
        return user


class ManagerClient(ServiceClient):
    def __init__(self, url: str, auth: "Auth | None" = None, timeout: int = 10) -> None:
        logger.debug(
            f"Connecting to manager instance at '{url}' using "
            f"auth class `{auth}`..."
        )
        super().__init__(url, auth=auth, timeout=timeout)

        self.check_root()

        self.model_permissions = BaseRepository(
            self, "modelpermissions", ModelPermission
        )
        self.ixmp4 = BaseRepository(self, "ixmp4", Ixmp4Instance)
        self.users = UserRepository(self)

    def make_http_client(self, url: str, auth: "Auth | None", timeout: int) -> None:
        logger.debug(f"Making new http service client for url={url} auth={auth}.")

        self.http_client = httpx.Client(
            base_url=url,
            timeout=timeout,
            http2=True,
            auth=auth,
            # We need to set this because the ICT proxy setup
            # does not set some headers properly, resulting in
            # django returning http urls instead of https urls
            # even if configured correctly.
            follow_redirects=True,
        )

    def check_root(self) -> None:
        """Requests root api endpoint and logs messages."""
        res = self.http_client.get("/")
        self.raise_service_exception(res)
        root = Root(**res.json())

        for warning in root.messages.get("warning", []):
            logger.warning(warning)

        for info in root.messages.get("info", []):
            logger.info(info)
