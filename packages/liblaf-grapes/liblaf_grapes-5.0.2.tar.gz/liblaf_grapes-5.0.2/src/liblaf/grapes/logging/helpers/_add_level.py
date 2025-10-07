import loguru._logger
from loguru import logger


def add_level(
    name: str, no: int | None = None, color: str | None = None, icon: str | None = None
) -> "loguru.Level":
    core: loguru._logger.Core = logger._core  # pyright: ignore[reportAttributeAccessIssue] # noqa: SLF001
    if name in core.levels and no == logger.level(name).no:
        no = None  # skip update severity no
    return logger.level(name=name, no=no, color=color, icon=icon)
