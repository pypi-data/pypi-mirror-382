import pydantic

from ._base import BaseConfig
from ._joblib import ConfigJoblib
from ._logging import ConfigLogging
from ._pretty import ConfigPretty
from ._traceback import ConfigTraceback


class Config(BaseConfig):
    joblib: ConfigJoblib = pydantic.Field(default_factory=ConfigJoblib)
    logging: ConfigLogging = pydantic.Field(default_factory=ConfigLogging)
    pretty: ConfigPretty = pydantic.Field(default_factory=ConfigPretty)
    traceback: ConfigTraceback = pydantic.Field(default_factory=ConfigTraceback)


config = Config()
