from pathlib import Path

import platformdirs
import pydantic
import pydantic_settings as ps

from ._base import BaseConfig


def _default_location() -> Path:
    return platformdirs.user_cache_path(appname="joblib")


class ConfigJoblibMemory(BaseConfig):
    model_config = ps.SettingsConfigDict(env_prefix="JOBLIB_MEMORY_")
    location: Path = pydantic.Field(default_factory=_default_location)
    bytes_limit: int | str | None = "4G"


class ConfigJoblib(BaseConfig):
    memory: ConfigJoblibMemory = pydantic.Field(default_factory=ConfigJoblibMemory)
