from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal, overload

from liblaf.grapes.typing import PathLike

from ._encode import EncHook, PydanticModelDumpOptions
from ._serde import json, toml, yaml

writers: dict[str, Callable] = {}
writers[".json"] = json.save
writers[".toml"] = toml.save
writers[".yaml"] = yaml.save
writers[".yml"] = yaml.save


@overload
def save(  # pyright: ignore[reportInconsistentOverload]
    path: PathLike,
    obj: Any,
    /,
    *,
    enc_hook: EncHook | None = ...,
    force_ext: str | None = None,
    order: Literal["deterministic", "sorted"] | None = None,
    pydantic: PydanticModelDumpOptions | None = None,
) -> None: ...
def save(path: PathLike, obj: Any, /, force_ext: str | None = None, **kwargs) -> None:
    path = Path(path)
    ext: str = force_ext or path.suffix
    return writers[ext](path, obj, **kwargs)
