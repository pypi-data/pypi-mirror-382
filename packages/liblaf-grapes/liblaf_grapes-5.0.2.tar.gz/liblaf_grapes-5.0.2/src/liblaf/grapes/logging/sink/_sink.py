import types
from collections.abc import Generator, Sequence

import attrs
import loguru
from rich.console import Console, RenderableType

from liblaf.grapes import pretty
from liblaf.grapes.logging.helpers import rich_traceback

from .columns import (
    RichSinkColumn,
    RichSinkColumnElapsed,
    RichSinkColumnLevel,
    RichSinkColumnLocation,
    RichSinkColumnMessage,
)


def default_columns(*, enable_link: bool = True) -> Sequence[RichSinkColumn]:
    return [
        RichSinkColumnElapsed(),
        RichSinkColumnLevel(),
        RichSinkColumnLocation(enable_link=enable_link),
        RichSinkColumnMessage(),
    ]


def default_console() -> Console:
    return pretty.get_console(stderr=True)


@attrs.define
class RichSink:
    columns: Sequence[RichSinkColumn] = attrs.field(
        converter=attrs.converters.default_if_none(factory=default_columns),
        factory=default_columns,
    )
    console: Console = attrs.field(
        converter=attrs.converters.default_if_none(factory=default_console),
        factory=default_console,
    )

    def __init__(
        self,
        columns: Sequence[RichSinkColumn] | None = None,
        console: Console | None = None,
        *,
        enable_link: bool = True,
    ) -> None:
        if columns is None:
            columns = default_columns(enable_link=enable_link)
        self.__attrs_init__(columns=columns, console=console)  # pyright: ignore[reportAttributeAccessIssue]

    def __call__(self, message: "loguru.Message", /) -> None:
        record: loguru.Record = message.record
        # TODO: `console.print()` is slow
        self.console.print(
            *self.render(record), overflow="ignore", no_wrap=True, crop=False
        )
        if (excpetion := self.render_exception(record)) is not None:
            self.console.print(excpetion)

    def render(self, record: "loguru.Record", /) -> Generator[RenderableType]:
        for column in self.columns:
            yield column.render(record)

    def render_exception(self, record: "loguru.Record", /) -> RenderableType | None:
        exception: loguru.RecordException | None = record["exception"]
        if exception is None:
            return None
        exc_type: type[BaseException] | None
        exc_value: BaseException | None
        traceback: types.TracebackType | None
        exc_type, exc_value, traceback = exception
        if exc_type is None or exc_value is None:
            return None
        return rich_traceback(exc_type, exc_value, traceback)
