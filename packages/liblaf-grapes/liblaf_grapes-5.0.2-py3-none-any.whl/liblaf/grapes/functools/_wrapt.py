from collections.abc import Callable
from typing import Any, Protocol, overload

import wrapt

from liblaf.grapes.sentinel import MISSING


class Decorator(Protocol):
    def __call__[T](self, wrapped: T, /) -> T: ...


class Wrapper(Protocol):
    def __call__(
        self, wrapped: Any, instance: Any, args: tuple, kwargs: dict[str, Any], /
    ) -> Any: ...


@overload
def decorator(
    wrapper: Wrapper,
    *,
    enabled: bool | Callable[[], None] | None = None,
    adapter: Any = None,
    proxy: Callable = ...,
) -> Decorator: ...
@overload
def decorator(
    *,
    enabled: bool | Callable[[], None] | None = None,
    adapter: Any = None,
    proxy: Callable = ...,
) -> Callable[[Wrapper], Decorator]: ...
def decorator(*args, **kwargs) -> Any:
    return wrapt.decorator(*args, **kwargs)


def wrapt_setattr(obj: Any, name: str, value: Any, /) -> None:
    name = f"_self_{name}"
    setattr(obj, name, value)


@overload
def wrapt_getattr(obj: Any, name: str, /) -> Any: ...
@overload
def wrapt_getattr[T](obj: Any, name: str, default: T, /) -> Any | T: ...
def wrapt_getattr(obj: Any, name: str, default: Any = MISSING, /) -> Any:
    name = f"_self_{name}"
    try:
        return getattr(obj, name)
    except AttributeError:
        parent: Any = getattr(obj, "_self_parent", None)
        if parent is None:
            if default is MISSING:
                raise
            return default
        if hasattr(parent, name):
            return getattr(parent, name)
        if default is MISSING:
            raise
        return default
