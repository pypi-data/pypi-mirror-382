import functools
import importlib.util


@functools.lru_cache
def has_module(name: str, package: str | None = None) -> bool:
    return importlib.util.find_spec(name, package) is not None
