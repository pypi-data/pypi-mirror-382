import functools
from collections.abc import Callable
from typing import Any, overload

import attrs

from ._wadler_lindig import pdoc_attrs, pformat


@overload
def auto_repr[T: type](
    cls: T, *, repr: bool | None = None, pdoc: bool | None = None
) -> T: ...
@overload
def auto_repr[T: type](
    *, repr: bool | None = None, pdoc: bool | None = None
) -> Callable[[T], T]: ...
def auto_repr(
    cls: type | None = None,
    *,
    repr: bool | None = None,  # noqa: A002
    pdoc: bool | None = None,
) -> Any:
    if cls is None:
        return functools.partial(auto_repr, repr=repr, pdoc=pdoc)
    if repr or (repr is None and "__repr__" not in cls.__dict__):
        cls.__repr__ = lambda self: pformat(self)  # pyright: ignore[reportAttributeAccessIssue]
    if (pdoc or (pdoc is None and "__pdoc__" not in cls.__dict__)) and attrs.has(cls):
        cls.__pdoc__ = pdoc_attrs  # pyright: ignore[reportAttributeAccessIssue]
    return cls
