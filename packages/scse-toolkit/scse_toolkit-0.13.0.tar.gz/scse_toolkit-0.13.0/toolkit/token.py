import json
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from uuid import uuid4

import jwt
from pydantic import BaseModel

from .exceptions import InvalidToken
from .manager.models import User

token_lifetime = timedelta(minutes=15)
token_leeway = 300
token_algorithm = "HS256"


class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"

    def __str__(self) -> str:
        return self.value


class Token(BaseModel):
    """Model used to serialize and validate the 'json' part of a JWT."""

    token_type: TokenType
    exp: int
    jti: str
    sub: str
    # TODO: The manager should return this.
    iss: str = "urn:iiasa:ece:scse-manager"
    user_id: int | None = None
    user: User | None = None

    @property
    def is_serviceaccount(self) -> bool:
        return self.user_id is None

    def dump(self) -> dict[str, object]:
        return self.model_dump(mode="json", exclude_none=True)

    def is_expired(self) -> bool:
        return self.exp < datetime.now().timestamp()

    def __hash__(self) -> int:
        dump = self.dump()
        return hash(json.dumps(dump, sort_keys=True))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Token):
            return hash(self) == hash(other)
        else:
            raise ValueError(
                f"Cannot compare `{self.__class__.__name__}` and `{other.__class__.__name__}`"
            )


class PreencodedToken(Token):
    encoded_str: str | None = None

    def dump(self) -> dict[str, object]:
        return self.model_dump(mode="json", exclude_none=True, exclude={"encoded_str"})


def get_exp() -> int:
    return int((datetime.now() + token_lifetime).timestamp())


def create(
    sub: str | User, issuer: str, token_type: TokenType = TokenType.access
) -> Token:
    """Creates a new token with fresh uuid and expiration timestamp.
    If `sub` is a `User` object a user token will be generated."""

    jti = uuid4().hex
    exp = get_exp()

    if isinstance(sub, User):
        user = sub
        user_id = sub.id
        sub = sub.username
    elif isinstance(sub, str):
        user = None
        user_id = None
    else:
        raise ValueError(
            f"`sub` must be either `str` or `User`, got `{sub.__class__.__name__}`"
        )

    token = Token(
        token_type=token_type,
        exp=exp,
        jti=jti,
        iss=f"urn:iiasa:ece:{issuer}",
        user=user,
        user_id=user_id,
        sub=sub,
    )
    return token


# TODO: remove this in the next bigger release
create_token = create


@lru_cache
def cached_encode(token: Token, secret: str) -> str:
    return jwt.encode(
        token.dump(),
        secret,
        algorithm=token_algorithm,
    )


def encode(token: Token, secret: str, refresh: bool = False) -> str:
    """Encodes the given token model into a header-ready string.
    If `refresh is `True` and the token has expired, it will be refreshed."""

    if refresh and token.is_expired():
        token.exp = get_exp()
    return cached_encode(token, secret)


def decode(token_str: str) -> PreencodedToken:
    """Decodes the given token string into a token model.
    Does not check the token for validity."""
    try:
        token_dict = jwt.decode(
            token_str,
            options={"verify_signature": False, "verify_exp": False},
            algorithms=[token_algorithm],
            leeway=token_leeway,
        )
    except jwt.InvalidTokenError:
        raise InvalidToken()
    return PreencodedToken(**token_dict, encoded_str=token_str)


def verify(token_str: str, secret: str) -> PreencodedToken:
    """Decodes the given token string into a token model
    and verifies expiration and signature."""
    try:
        token_dict = jwt.decode(
            token_str,
            secret,
            algorithms=[token_algorithm],
            leeway=token_leeway,
        )
    except jwt.InvalidTokenError:
        raise InvalidToken()
    return PreencodedToken(**token_dict, encoded_str=token_str)
