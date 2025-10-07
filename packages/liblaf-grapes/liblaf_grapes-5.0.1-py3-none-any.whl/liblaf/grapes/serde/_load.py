from collections.abc import Callable
from pathlib import Path
from typing import Any, overload

from liblaf.grapes.typing import PathLike

from ._decode import DecHook, PydanticModelValidateOptions
from ._serde import json, toml, yaml

readers: dict[str, Callable] = {}
readers[".json"] = json.load
readers[".toml"] = toml.load
readers[".yaml"] = yaml.load
readers[".yml"] = yaml.load


@overload
def load(
    path: PathLike,
    /,
    *,
    dec_hook: DecHook | None = ...,
    force_ext: str | None = None,
    pydantic: PydanticModelValidateOptions | None = None,
    strict: bool = True,
) -> Any: ...
@overload
def load[T](
    path: PathLike,
    /,
    *,
    dec_hook: DecHook | None = ...,
    force_ext: str | None = None,
    pydantic: PydanticModelValidateOptions | None = None,
    strict: bool = True,
    type: type[T],
) -> T: ...
@overload
def load[T](
    path: PathLike,
    /,
    *,
    dec_hook: DecHook | None = ...,
    force_ext: str | None = None,
    pydantic: PydanticModelValidateOptions | None = None,
    strict: bool = True,
    type: Any,
) -> Any: ...
def load(path: PathLike, /, *, force_ext: str | None = None, **kwargs) -> Any:
    path = Path(path)
    ext: str = force_ext or path.suffix
    return readers[ext](path, **kwargs)
