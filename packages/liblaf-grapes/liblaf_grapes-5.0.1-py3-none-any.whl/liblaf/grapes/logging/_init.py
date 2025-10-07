from collections.abc import Mapping, Sequence
from typing import Any

import loguru
import toolz
from loguru import logger

from liblaf.grapes.conf import config
from liblaf.grapes.typing import PathLike

from .filters import FilterLike
from .handlers import file_handler, rich_handler
from .helpers import (
    setup_excepthook,
    setup_icecream,
    setup_loguru_intercept,
    setup_unraisablehook,
)


def init(
    *,
    enable_link: bool = True,
    file: PathLike | None = None,
    filter: FilterLike = None,  # noqa: A002
    handlers: Sequence["loguru.HandlerConfig"] | None = None,
    intercept: bool = True,
    level: int | str | None = None,
) -> None:
    if file is None:
        file = config.logging.file
    if level is None:
        level = config.logging.level

    if handlers is None:
        handler_config: Mapping[str, Any] = toolz.valfilter(
            lambda v: v is not None, {"filter": filter, "level": level}
        )
        handlers: list[loguru.HandlerConfig] = [
            rich_handler(**handler_config, enable_link=enable_link)
        ]
        if file:
            handlers.append(file_handler(sink=file, **handler_config))
    logger.configure(handlers=handlers)

    setup_excepthook()
    setup_icecream()
    setup_unraisablehook()
    if intercept:
        setup_loguru_intercept(level=level)
