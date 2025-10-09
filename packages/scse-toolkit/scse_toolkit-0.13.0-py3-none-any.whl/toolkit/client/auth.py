import logging
from typing import Iterator

import httpx

from toolkit.exceptions import InvalidCredentials
from toolkit.manager import ManagerClient
from toolkit.manager.models import User
from toolkit.token import PreencodedToken, Token, create, decode, encode

logger = logging.getLogger(__file__)


class Auth(httpx.Auth):
    access_token: Token | None

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"


class PreencodedTokenAuth(Auth):
    """Can be used by a service to "impersonate" or "proxy" incoming tokens."""

    def __init__(self, secret: str, token: PreencodedToken | None):
        self.access_token = token
        self.secret = secret

    def set_token(self, token: PreencodedToken | None) -> None:
        self.access_token = token

    def unset_token(self) -> None:
        self.access_token = None

    def auth_flow(self, r: httpx.Request) -> Iterator[httpx.Request]:
        if self.access_token is None:
            yield r
        else:
            r.headers["Authorization"] = "Bearer " + encode(
                self.access_token, self.secret, refresh=True
            )
            yield r


class SelfSignedAuth(Auth):
    """Generates its own JWT with the supplied secret."""

    access_token: Token

    def __init__(
        self,
        secret: str,
        issuer: str = "scse-toolkit",
        sub: str | User = "@self-signed",
    ):
        self.secret = secret
        self.access_token = create(sub, issuer)

    def auth_flow(self, r: httpx.Request) -> Iterator[httpx.Request]:
        r.headers["Authorization"] = "Bearer " + encode(
            self.access_token, self.secret, refresh=True
        )
        yield r


class ManagerAuth(Auth):
    """Uses the SceSe Management Service to obtain and refresh a token."""

    refresh_token: PreencodedToken
    access_token: PreencodedToken

    def __init__(
        self,
        username: str,
        password: str,
        url: str,
    ):
        self.client = httpx.Client(base_url=url, http2=True)
        self.username = username
        self.password = password
        self.obtain_jwt()

    def auth_flow(self, r: httpx.Request) -> Iterator[httpx.Request]:
        if self.access_token.is_expired():
            self.refresh_or_reobtain_jwt()

        if self.access_token.encoded_str is None:
            raise ValueError("`Token.encoded_str` must be set.")

        r.headers["Authorization"] = "Bearer " + self.access_token.encoded_str
        yield r

    def obtain_jwt(self) -> None:
        res = self.client.post(
            "/token/obtain/",
            json={
                "username": self.username,
                "password": self.password,
            },
        )
        if res.status_code >= 400:
            if res.status_code == 401:
                raise InvalidCredentials()
            else:
                res.raise_for_status()

        json = res.json()
        self.access_token = decode(json["access"])
        self.refresh_token = decode(json["refresh"])

    def refresh_or_reobtain_jwt(self) -> None:
        if self.refresh_token.is_expired():
            self.obtain_jwt()
        else:
            self.refresh_jwt()

    def refresh_jwt(self) -> None:
        res = self.client.post(
            "/token/refresh/",
            json={
                "refresh": self.refresh_token.encoded_str,
            },
        )
        res.raise_for_status()
        self.access_token = decode(res.json()["access"])


class ImpersonatingAuth(ManagerAuth):
    """Impersonates a user by using a self-signed admin
    token and the management service's impersonation endpoint.
    Requires knowledge of the system secret."""

    def __init__(
        self,
        url: str,
        secret: str,
        user_id: int,
    ):
        self.admin_client = ManagerClient(url, SelfSignedAuth(secret))
        self.user_id = user_id
        self.obtain_jwt()
        self.client = httpx.Client(base_url=url, http2=True)

    def obtain_jwt(self) -> None:
        json = self.admin_client.users.impersonate(self.user_id)
        self.access_token = decode(json["access"])
        self.refresh_token = decode(json["refresh"])
