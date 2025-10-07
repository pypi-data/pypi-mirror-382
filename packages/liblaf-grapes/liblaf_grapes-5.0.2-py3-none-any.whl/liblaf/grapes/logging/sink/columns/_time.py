import datetime

import attrs
import loguru
from rich.console import RenderableType
from rich.text import Text

from ._abc import RichSinkColumn


@attrs.define
class RichSinkColumnTime(RichSinkColumn):
    fmt: str = "%Y-%m-%dT%H:%M:%S.%f"

    def render(self, record: "loguru.Record", /) -> RenderableType:
        time: datetime.datetime = record["time"]
        return Text(f"{time:{self.fmt}}", style="log.time")
