import inspect
import itertools
import logging
import types
from collections.abc import Iterable

import loguru._logger
from loguru import logger


def clear_stdlib_handlers() -> None:
    for std_logger in logging.root.manager.loggerDict.values():
        if isinstance(std_logger, logging.PlaceHolder):
            continue
        std_logger.handlers.clear()
        std_logger.propagate = True


def setup_loguru_intercept(
    level: int | str = logging.NOTSET, modules: Iterable[str] = ()
) -> None:
    """Logs to loguru from Python logging module.

    References:
        1. [Entirely compatible with standard logging](https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging)
        2. [loguru-logging-intercept/loguru_logging_intercept.py at f358b75ef4162ea903bf7a3298c22b1be83110da · MatthewScholefield/loguru-logging-intercept](https://github.com/MatthewScholefield/loguru-logging-intercept/blob/f358b75ef4162ea903bf7a3298c22b1be83110da/loguru_logging_intercept.py)
    """
    core: loguru._logger.Core = logger._core  # pyright: ignore[reportAttributeAccessIssue] # noqa: SLF001
    for loguru_level in core.levels.values():
        logging.addLevelName(loguru_level.no, loguru_level.name)
    if isinstance(level, str):
        level = logger.level(level).no
    logging.basicConfig(handlers=[InterceptHandler()], level=level)
    clear_stdlib_handlers()
    for logger_name in itertools.chain(("",), modules):
        mod_logger: logging.Logger = logging.getLogger(logger_name)
        mod_logger.handlers = [InterceptHandler()]
        mod_logger.propagate = False


class InterceptHandler(logging.Handler):
    """Logs to loguru from Python logging module.

    References:
        1. [Entirely compatible with standard logging](https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging)
        2. [loguru-logging-intercept/loguru_logging_intercept.py at f358b75ef4162ea903bf7a3298c22b1be83110da · MatthewScholefield/loguru-logging-intercept](https://github.com/MatthewScholefield/loguru-logging-intercept/blob/f358b75ef4162ea903bf7a3298c22b1be83110da/loguru_logging_intercept.py)
    """

    def emit(self, record: logging.LogRecord) -> None:
        if logger is None:  # logger has been cleaned up
            return

        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame: types.FrameType | None = inspect.currentframe()
        depth: int = 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
