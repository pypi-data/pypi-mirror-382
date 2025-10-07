import contextlib
from collections.abc import Generator
from typing import Any, Self

import pydantic
import pydantic_settings as ps


class OverridesMixin:
    @contextlib.contextmanager
    def overrides(self, **kwargs) -> Generator[Self]:
        backup: dict[str, Any] = {}
        for k, v in kwargs.items():
            backup[k] = getattr(self, k)
            setattr(self, k, v)
        try:
            yield self
        finally:
            for k, v in backup.items():
                setattr(self, k, v)


class BaseConfig(OverridesMixin, ps.BaseSettings):
    model_config = ps.SettingsConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True, validate_default=True
    )


class BaseModel(OverridesMixin, pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True, validate_default=True
    )
