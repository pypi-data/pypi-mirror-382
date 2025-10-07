import contextlib
from collections.abc import Generator

from etils import epy


@contextlib.contextmanager
def optional_imports(package: str, extra: str) -> Generator[None]:
    try:
        yield
    except ImportError as err:
        epy.reraise(
            err, suffix=f"Make sure to install `{package}` with the `{extra}` extra."
        )
