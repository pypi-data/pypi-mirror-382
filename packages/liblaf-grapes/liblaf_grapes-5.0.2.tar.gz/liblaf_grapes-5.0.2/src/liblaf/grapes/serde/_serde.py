import functools
from collections.abc import Buffer, Callable
from pathlib import Path
from typing import Any, Literal, overload

import attrs
import msgspec

from liblaf.grapes.typing import PathLike

from ._decode import DecHook, PydanticModelValidateOptions, dec_hook
from ._encode import EncHook, PydanticModelDumpOptions, enc_hook

type Decoder = Callable
type Encoder = Callable


@attrs.define
class Serde:
    decoder: Decoder
    encoder: Encoder

    @overload
    def decode(
        self,
        buf: Buffer | str,
        /,
        *,
        dec_hook: DecHook | None = ...,
        pydantic: PydanticModelValidateOptions | None = None,
        strict: bool = True,
    ) -> Any: ...
    @overload
    def decode[T](
        self,
        buf: Buffer | str,
        /,
        *,
        dec_hook: DecHook | None = ...,
        pydantic: PydanticModelValidateOptions | None = None,
        strict: bool = True,
        type: type[T],
    ) -> T: ...
    @overload
    def decode[T](
        self,
        buf: Buffer | str,
        /,
        *,
        dec_hook: DecHook | None = ...,
        pydantic: PydanticModelValidateOptions | None = None,
        strict: bool = True,
        type: Any,
    ) -> Any: ...
    def decode(self, buf: Buffer | str, /, **kwargs) -> Any:
        if "dec_hook" not in kwargs:
            kwargs["dec_hook"] = functools.partial(
                dec_hook, pydantic_options=kwargs.pop("pydantic", None)
            )
        return self.decoder(buf, **kwargs)

    @overload
    def encode(  # pyright: ignore[reportInconsistentOverload]
        self,
        obj: Any,
        /,
        *,
        enc_hook: EncHook | None = ...,
        order: Literal["deterministic", "sorted"] | None = None,
        pydantic: PydanticModelDumpOptions | None = None,
    ) -> bytes: ...
    def encode(self, obj: Any, /, **kwargs) -> bytes:
        if "enc_hook" not in kwargs:
            kwargs["enc_hook"] = functools.partial(
                enc_hook, pydantic_options=kwargs.pop("pydantic", None)
            )
        return self.encoder(obj, **kwargs)

    @overload
    def load(
        self,
        path: PathLike,
        /,
        *,
        dec_hook: DecHook | None = ...,
        pydantic: PydanticModelValidateOptions | None = None,
        strict: bool = True,
    ) -> Any: ...
    @overload
    def load[T](
        self,
        path: PathLike,
        /,
        *,
        dec_hook: DecHook | None = ...,
        pydantic: PydanticModelValidateOptions | None = None,
        strict: bool = True,
        type: type[T],
    ) -> T: ...
    @overload
    def load[T](
        self,
        path: PathLike,
        /,
        *,
        dec_hook: DecHook | None = ...,
        pydantic: PydanticModelValidateOptions | None = None,
        strict: bool = True,
        type: Any,
    ) -> Any: ...
    def load(self, path: PathLike, /, **kwargs) -> Any:
        path = Path(path)
        return self.decode(path.read_bytes(), **kwargs)

    @overload
    def save(  # pyright: ignore[reportInconsistentOverload]
        self,
        path: PathLike,
        obj: Any,
        /,
        *,
        enc_hook: EncHook | None = ...,
        order: Literal["deterministic", "sorted"] | None = None,
        pydantic: PydanticModelDumpOptions | None = None,
    ) -> None: ...
    def save(self, path: PathLike, obj: Any, /, **kwargs) -> None:
        path = Path(path)
        path.write_bytes(self.encode(obj, **kwargs))


json = Serde(decoder=msgspec.json.decode, encoder=msgspec.json.encode)
toml = Serde(decoder=msgspec.toml.decode, encoder=msgspec.toml.encode)
yaml = Serde(decoder=msgspec.yaml.decode, encoder=msgspec.yaml.encode)
