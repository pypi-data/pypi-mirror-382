import functools
import time
from importlib import import_module
from typing import Any, Callable, Generic, Hashable, ParamSpec, Protocol, TypeVar


def import_member(member_str: str) -> tuple[Any, tuple[str, str]]:
    module_name, member_name = member_str.rsplit(":", 1)
    module = import_module(module_name)
    obj: object | None = getattr(module, member_name, None)
    return obj, (member_name, module_name)


ReturnT = TypeVar("ReturnT", covariant=True)
Params = ParamSpec("Params")


class CachableCallable(Generic[Params, ReturnT], Protocol):
    def __call__(self, *args: Params.args, **kwargs: Params.kwargs) -> ReturnT: ...


def ttl_cache(
    ttl_seconds: int = 60 * 15, maxsize: int | None = 128, typed: bool = False
) -> Callable[
    [CachableCallable[Params, ReturnT]],
    Callable[
        ...,
        ReturnT,
    ],
]:
    """Caches a functions results for a fixed period of time using `functools.lru_cache`"""

    def decorator(
        func: CachableCallable[Params, ReturnT],
    ) -> Callable[
        ...,
        ReturnT,
    ]:
        def get_ttl_hash() -> int:
            """Return the same value for every time period of `ttl_seconds`."""
            return round(time.time() / ttl_seconds)

        # Note: We cannot type this function properly with `Params` because
        # of this limitation in PEP 612:
        # "Placing keyword-only parameters between the *args and **kwargs is forbidden."
        # https://peps.python.org/pep-0612/#concatenating-keyword-parameters

        @functools.lru_cache(maxsize=maxsize, typed=typed)
        def ttl_func(
            *args: Any,
            ttl_hash: int | None = None,
            **kwargs: Any,
        ) -> ReturnT:
            del ttl_hash
            return func(*args, **kwargs)

        @functools.wraps(func)
        def wrapper(*args: Hashable, **kwargs: Hashable) -> ReturnT:
            return ttl_func(*args, ttl_hash=get_ttl_hash(), **kwargs)

        return wrapper

    return decorator
