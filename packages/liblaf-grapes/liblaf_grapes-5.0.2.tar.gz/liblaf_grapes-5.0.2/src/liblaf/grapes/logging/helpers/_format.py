import types

import loguru
from rich.console import Console
from rich.traceback import Traceback

from liblaf.grapes import pretty

from ._traceback import rich_traceback

DEFAULT_FORMAT = (
    "<green>{elapsed}</green> "
    "<level>{level:<8}</level> "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "<level>{message}</level>"
)


def new_format(template: str = DEFAULT_FORMAT) -> "loguru.FormatFunction":
    template = template.strip() + "\n"

    def format_(record: "loguru.Record", /) -> str:
        if record["exception"] is None:
            return template
        exc_type: type[BaseException] | None
        exc_value: BaseException | None
        traceback: types.TracebackType | None
        exc_type, exc_value, traceback = record["exception"]
        if exc_type is None or exc_value is None:
            return template + "{exception}\n"
        console: Console = pretty.get_console(color_system=None)
        rich_tb: Traceback = rich_traceback(exc_type, exc_value, traceback, width=128)
        with console.capture() as capture:
            console.print(rich_tb)
        record["extra"]["rich_traceback"] = capture.get()
        return template + "{extra[rich_traceback]}\n"

    return format_
