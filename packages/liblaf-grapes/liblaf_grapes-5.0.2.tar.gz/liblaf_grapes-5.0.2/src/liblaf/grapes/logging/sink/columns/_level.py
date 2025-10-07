from typing import override

import loguru
from rich.console import RenderableType
from rich.text import Text

from ._abc import RichSinkColumn


class RichSinkColumnLevel(RichSinkColumn):
    width: int = 1

    @override  # impl RichSinkColumn
    def render(self, record: "loguru.Record", /) -> RenderableType:
        level: str = record["level"].name
        return Text(f"{level:<.{self.width}}", style=f"logging.level.{level.lower()}")
