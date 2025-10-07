from collections.abc import Callable, Mapping, Sequence

import attrs


@attrs.define
class Params:
    args: Sequence = ()
    kwargs: Mapping = {}


@attrs.define
class DispatchLookupError(LookupError):
    func: Callable
    params: Params

    def __init__(
        self, func: Callable, args: Sequence = (), kwargs: Mapping = {}
    ) -> None:
        params = Params(args=args, kwargs=kwargs)
        self.__attrs_init__(func=func, params=params)  # pyright: ignore[reportAttributeAccessIssue]

    def __str__(self) -> str:
        from liblaf.grapes import pretty

        pretty_call: str = pretty.pretty_call(
            self.func, self.params.args, self.params.kwargs
        )
        return f"`{pretty_call}` could not be resolved."
