import functools
import types
from collections.abc import Mapping

import loguru

from ._composite import CompositeFilter
from .typing import FilterLike


@functools.singledispatch
def new_filter(f: FilterLike, /) -> FilterLike:
    return f


@new_filter.register(types.NoneType)
def _new_filter_none(_: None, /) -> "loguru.FilterFunction":
    return CompositeFilter()


@new_filter.register(Mapping)
def _new_filter_mapping(by_level: "loguru.FilterDict", /) -> "loguru.FilterFunction":
    return CompositeFilter(by_level=by_level)
