import functools
from collections.abc import Callable
from typing import Any, TypedDict, Unpack

import attrs
import cytoolz as toolz
import wadler_lindig as wl

from liblaf.grapes.conf import config
from liblaf.grapes.typing import array_kind

from ._console import get_console

UNINITIALIZED = wl.TextDoc("<uninitialized>")


class WadlerLindigOptions(TypedDict, total=False):
    width: int | None
    indent: int
    short_arrays: bool
    custom: Callable[[Any], wl.AbstractDoc | None]
    hide_defaults: bool
    show_type_module: bool
    show_dataclass_module: bool
    show_function_module: bool
    respect_pdoc: bool
    short_arrays_threshold: int


def pdoc_attrs(self: Any, **kwargs: Unpack[WadlerLindigOptions]) -> wl.AbstractDoc:
    """.

    References:
        1. <https://github.com/patrick-kidger/wadler_lindig/blob/0226340d56f0c18e10cd4d375cf7ea25818359b8/wadler_lindig/_definitions.py#L308-L326>
    """
    kwargs: WadlerLindigOptions = _make_kwargs(kwargs)
    cls: type = type(self)
    objs: list[tuple[str, Any]] = []
    for field in attrs.fields(cls):
        field: attrs.Attribute
        if not field.repr:
            continue
        value: Any = getattr(self, field.name, UNINITIALIZED)
        if kwargs.get("hide_defaults", True) and value is field.default:
            continue
        objs.append((field.name, value))
    name_kwargs: dict[str, Any] = toolz.assoc(
        kwargs, "show_type_module", kwargs.get("show_dataclass_module", False)
    )
    return wl.bracketed(
        begin=wl.pdoc(cls, **name_kwargs) + wl.TextDoc("("),
        docs=wl.named_objs(objs, **kwargs),
        sep=wl.comma,
        end=wl.TextDoc(")"),
        indent=kwargs.get("indent", 2),
    )


@functools.singledispatch
def pdoc_custom(
    obj: Any, **kwargs: Unpack[WadlerLindigOptions]
) -> wl.AbstractDoc | None:
    if hasattr(obj, "__pdoc__"):
        return None
    if attrs.has(type(obj)):
        return pdoc_attrs(obj, **kwargs)
    if array_kind(obj):
        if kwargs.get("short_arrays") is None:
            kwargs["short_arrays"] = obj.size > kwargs.get(
                "short_arrays_threshold", 100
            )
        return wl.pdoc(obj, **kwargs)
    return None


@functools.singledispatch
def pformat(obj: Any, **kwargs: Unpack[WadlerLindigOptions]) -> str:
    kwargs: WadlerLindigOptions = _make_kwargs(kwargs)
    if kwargs.get("width") is None:
        kwargs["width"] = get_console(stderr=True).width
    if kwargs.get("custom") is None:
        kwargs["custom"] = functools.partial(pdoc_custom, **kwargs)
    return wl.pformat(obj, **kwargs)  # pyright: ignore[reportArgumentType]


def _make_kwargs(kwargs: WadlerLindigOptions) -> WadlerLindigOptions:
    kwargs: WadlerLindigOptions = toolz.merge(config.pretty.model_dump(), kwargs)
    return kwargs
