import sys
import types
from typing import Any

from loguru import logger


def setup_excepthook(level: int | str = "CRITICAL", message: Any = "") -> None:
    def excepthook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: types.TracebackType | None,
        /,
    ) -> None:
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).log(level, message)

    sys.excepthook = excepthook
