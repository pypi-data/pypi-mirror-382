from collections.abc import Callable
from typing import Any

import liblaf.grapes.functools as ft
from liblaf.grapes import pretty
from liblaf.grapes.logging import depth_tracker

from ._base import BaseTimer
from ._utils import set_timer


def timed_callable[C: Callable](func: C, timer: BaseTimer) -> C:
    if timer.name is None:
        timer.name = pretty.pretty_func(func)

    @ft.decorator
    @depth_tracker
    def wrapper(wrapped: C, _instance: Any, args: tuple, kwargs: dict[str, Any]) -> Any:
        timer.start()
        try:
            return wrapped(*args, **kwargs)
        finally:
            timer.stop()

    func: C = wrapper(func)
    set_timer(func, timer)
    return func
