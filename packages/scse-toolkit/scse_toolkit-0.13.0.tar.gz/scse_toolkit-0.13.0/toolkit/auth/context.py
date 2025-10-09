import functools
import re
from typing import Any, Callable, ParamSpec, cast, Protocol, runtime_checkable

import polars as pl

from toolkit.exceptions import Forbidden, PlatformNotFound
from toolkit.manager.client import ManagerClient
from toolkit.manager.models import AccessType, Accessibility, User

P = ParamSpec("P")


@runtime_checkable
class PlatformProtocol(Protocol):
    id: int
    access_group: int
    management_group: int
    accessibility: str


def raise_or_return(
    func: Callable[P, bool],
) -> Callable[..., bool]:
    """Decorator which adds an optional keyword argument `raise_exc` to the decorated function.
    If `raise_exc` is `True` or an exception or exception class, the/ an exception will be raised if the function returns a 'falsy' value.
    By default the raised exception is `Forbidden`."""

    @functools.wraps(func)
    def wrapper(
        *args: Any,
        raise_exc: bool | type[Exception] | Exception = False,
        **kwargs: Any,
    ) -> bool:
        raise_or_exc: bool | type[Exception] | Exception = raise_exc

        is_exc = False
        if isinstance(raise_or_exc, Exception):
            is_exc = True

        if isinstance(raise_or_exc, type) and issubclass(raise_or_exc, Exception):
            is_exc = True

        is_valid = isinstance(raise_or_exc, bool) or is_exc

        if not is_valid:
            raise ValueError("Named argument 'raise' must be `bool` or `Exception`.")

        exc: Exception = Forbidden()
        if raise_or_exc and is_exc:
            exc = cast(Exception, raise_or_exc)

        result = func(*args, **kwargs)
        if raise_or_exc and not result:
            raise exc
        else:
            return result

    return wrapper


class AuthorizationContext(object):
    """
    A context class that encapsulates the authorization logic for a user interacting with a platform.

    This class handles checking whether a user has permissions for various actions (e.g., view, edit, submit)
    on a given platform. It takes into account the user's roles, the platform's access restrictions, and the
    specific permissions granted to the user or groups the user belongs to.

    Attributes:
        user (User | None): The user associated with the context, or None if no user is specified.
        manager_client (ManagerClient): The client responsible for managing permissions and platform interactions.
    """

    user: User | None
    manager_client: ManagerClient

    def __init__(self, user: User | None, manager_client: ManagerClient):
        self.user = user
        self.manager_client = manager_client

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} user={self.user} manager={self.manager_client.url}>"

    def tabulate_permissions(self, platform: PlatformProtocol) -> pl.DataFrame:
        if self.user is not None:
            df = self.manager_client.model_permissions.cached_tabulate(
                instance=platform.id,
                group__users=self.user.id,
            )
        else:
            df = pl.DataFrame()

        # check `.value`/str() so the check doesnt fail with two different `Accessibility` enums
        if str(platform.accessibility) != str(Accessibility.PRIVATE):
            group_df = self.manager_client.model_permissions.cached_tabulate(
                instance=platform.id, group=platform.access_group
            )
            if df.is_empty() and group_df.is_empty():
                pass
            elif df.is_empty():
                df = group_df
            else:
                df = pl.concat([df, group_df])

        if df.is_empty():
            return df

        df = df.with_columns(
            pl.col("model")
            .map_elements(re.escape, pl.String)
            .str.replace_all(r"\\\*", ".*")
            .alias("regex"),
            pl.col("model").replace("*", "%").replace("_", "[_]").alias("like"),
        )

        return df

    def ensure_platform(self, platform: PlatformProtocol | str) -> PlatformProtocol:
        if isinstance(platform, PlatformProtocol):
            return platform

        try:
            [ixmp4instance] = self.manager_client.ixmp4.list(slug=platform)
            return ixmp4instance
        except ValueError as e:
            raise PlatformNotFound(
                f"Platform with slug '{platform}' was not found."
            ) from e

    def has_permission(
        self,
        platform: PlatformProtocol | str,
        acceptable_access_types: list[AccessType],
        models: list[str] | None = None,
    ) -> bool:
        platform = self.ensure_platform(platform)

        if self.user is not None:
            if self.user.is_superuser:
                return True
            if platform.management_group in self.user.groups:
                return True

        df = self.tabulate_permissions(platform)
        if df.is_empty():
            return False

        df = df.filter(
            pl.col("access_type").is_in([str(aat) for aat in acceptable_access_types])
        )

        if models is not None:
            regex = re.compile("^" + "|".join(df["regex"]) + "$")
            for model in models:
                if regex.match(model) is None:
                    return False

        return not df.is_empty()

    @raise_or_return
    def has_management_permission(self, platform: PlatformProtocol | str) -> bool:
        """
        Checks whether the user is a platform manager.

        Args:
            platform (PlatformProtocol | str): The platform to check the user's permissions against.

        Returns:
            bool: True if the user has management permission, False otherwise.
        """
        platform = self.ensure_platform(platform)

        if self.user is None:
            return False
        if self.user.is_superuser:
            return True

        return platform.management_group in self.user.groups

    @raise_or_return
    def has_edit_permission(
        self, platform: PlatformProtocol | str, models: list[str] | None = None
    ) -> bool:
        """
        Checks whether the user has permission to edit on the platform.

        Args:
            platform (Ixmp4Instance): The platform to check the user's permissions against.
            models (list[str] | None): A list of model names to check the user's permissions for,
            or None to check permissions for any models.

        Returns:
            bool: True if the user has edit permission, False otherwise.
        """

        return self.has_permission(platform, [AccessType.EDIT], models=models)

    @raise_or_return
    def has_submit_permission(
        self, platform: PlatformProtocol | str, models: list[str] | None = None
    ) -> bool:
        """
        Checks whether the user has permission to submit on the platform.

        Args:
            platform (PlatformProtocol | str): The platform to check the user's permissions against.
            models (list[str] | None): A list of model names to check the user's permissions for,
            or None to check permissions for any models.

        Returns:
            bool: True if the user has submit permission, False otherwise.
        """

        return self.has_permission(
            platform, [AccessType.EDIT, AccessType.SUBMIT], models=models
        )

    @raise_or_return
    def has_view_permission(
        self, platform: PlatformProtocol | str, models: list[str] | None = None
    ) -> bool:
        """
        Checks whether the user has permission to view model runs on the platform.

        Args:
            platform (PlatformProtocol | str): The platform to check the user's permissions against.
            models (list[str] | None): A list of model names to check the user's permissions for,
            or None to check permissions for any models.

        Returns:
            bool: True if the user has view permission, False otherwise.
        """

        return self.has_permission(
            platform,
            [AccessType.EDIT, AccessType.SUBMIT, AccessType.VIEW],
            models=models,
        )

    @raise_or_return
    def is_authenticated(self) -> bool:
        """
        Checks whether the user is authenticated.

        Returns:
            bool: True if the user is authenticated, False otherwise.
        """
        if self.user is None:
            return False

        return self.user.is_authenticated

    @raise_or_return
    def is_verified(self) -> bool:
        """
        Checks whether the user is verified.

        Returns:
            bool: True if the user is verified, False otherwise.
        """
        if not self.is_authenticated():
            return False
        assert self.user is not None
        return self.user.is_verified

    @raise_or_return
    def is_staff(self) -> bool:
        """
        Checks whether the user is a staff member.

        Returns:
            bool: True if the user is a staff member, False otherwise.
        """
        if not self.is_authenticated():
            return False
        assert self.user is not None
        return self.user.is_staff

    @raise_or_return
    def is_superuser(self) -> bool:
        """
        Checks whether the user is a superuser.

        Returns:
            bool: True if the user is a superuser, False otherwise.
        """
        if not self.is_authenticated():
            return False
        assert self.user is not None
        return self.user.is_superuser
