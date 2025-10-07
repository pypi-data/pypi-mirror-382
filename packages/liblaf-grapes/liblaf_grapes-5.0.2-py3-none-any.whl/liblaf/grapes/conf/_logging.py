from pathlib import Path

import pydantic_settings as ps

from ._base import BaseConfig


class ConfigLogging(BaseConfig):
    model_config = ps.SettingsConfigDict(env_prefix="LOG_")
    file: Path | None = None
    level: int | str = "TRACE"
