from typing import Any

import liblaf.grapes.functools as ft

from ._base import BaseTimer


def get_timer(wrapper: Any) -> BaseTimer:
    return ft.wrapt_getattr(wrapper, "timer")


def set_timer(wrapper: Any, timer: BaseTimer) -> None:
    ft.wrapt_setattr(wrapper, "timer", timer)
