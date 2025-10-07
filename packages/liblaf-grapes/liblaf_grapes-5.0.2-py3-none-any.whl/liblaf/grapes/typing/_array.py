import sys
from typing import Any


def array_kind(obj: Any) -> str | None:
    for module, typename in [
        ("numpy", "ndarray"),
        ("torch", "Tensor"),
        ("jax", "Array"),
        ("mlx.core", "array"),
    ]:
        if module not in sys.modules:
            continue
        typ: type = getattr(sys.modules[module], typename)
        if isinstance(obj, typ):
            return module
    return None
