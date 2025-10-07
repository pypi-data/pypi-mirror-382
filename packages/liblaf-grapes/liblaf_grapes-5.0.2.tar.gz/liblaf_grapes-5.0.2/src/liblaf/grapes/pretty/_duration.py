import math

from liblaf.grapes.error import MatchError

FORMATS: list[tuple[int, float, str]] = [
    (11, 1e-8, "9.99 ns"),
    (10, 1e-7, "99.9 ns"),
    (9, 1e-6, "999. ns"),
    (8, 1e-5, "9.99 µs"),
    (7, 1e-4, "99.9 µs"),
    (6, 1e-3, "999. µs"),
    (5, 1e-2, "9.99 ms"),
    (4, 1e-1, "99.9 ms"),
    (3, 1.0, "999. ms"),
    (2, 1e1, "9.99 s"),
    (1, 60, "99.9 s"),
    (0, 3600.0, "59:59"),
    (0, 86400.0, "23:59:59"),
    (0, math.inf, "1d,23:59:59"),
]


def choose_duration_format(seconds: float) -> str:
    for prec, threshold, fmt in FORMATS:
        if round(seconds, prec) < threshold:
            return fmt
    raise NotImplementedError


def pretty_duration(seconds: float, fmt: str | None = None) -> str:  # noqa: C901, PLR0911, PLR0912
    """.

    Examples:
        >>> pretty_duration(math.nan)
        '?? s'
        >>> pretty_duration(1e-12)
        '0.00 ns'
        >>> pretty_duration(1e-11)
        '0.01 ns'
        >>> pretty_duration(1e-10)
        '0.10 ns'
        >>> pretty_duration(1e-9)
        '1.00 ns'
        >>> pretty_duration(1e-8)
        '10.0 ns'
        >>> pretty_duration(1e-7)
        '100. ns'
        >>> pretty_duration(1e-6)
        '1.00 µs'
        >>> pretty_duration(1e-5)
        '10.0 µs'
        >>> pretty_duration(1e-4)
        '100. µs'
        >>> pretty_duration(1e-3)
        '1.00 ms'
        >>> pretty_duration(1e-2)
        '10.0 ms'
        >>> pretty_duration(1e-1)
        '100. ms'
        >>> pretty_duration(1.0)
        '1.00 s'
        >>> pretty_duration(1e1)
        '10.0 s'
        >>> pretty_duration(1e2)
        '01:40'
        >>> pretty_duration(1e3)
        '16:40'
        >>> pretty_duration(1e4)
        '02:46:40'
        >>> pretty_duration(1e5)
        '1d,03:46:40'
        >>> pretty_duration(1e6)
        '11d,13:46:40'
    """
    if not math.isfinite(seconds):
        return "?? s"
    if fmt is None:
        fmt = choose_duration_format(seconds)
    fmt = fmt.replace("us", "µs")
    match fmt:
        case "9.99 ns":
            return f"{seconds * 1e9:#.2f} ns"
        case "99.9 ns":
            return f"{seconds * 1e9:#.1f} ns"
        case "999. ns":
            return f"{seconds * 1e9:#.0f} ns"
        case "9.99 µs":
            return f"{seconds * 1e6:#.2f} µs"
        case "99.9 µs":
            return f"{seconds * 1e6:#.1f} µs"
        case "999. µs":
            return f"{seconds * 1e6:#.0f} µs"
        case "9.99 ms":
            return f"{seconds * 1e3:#.2f} ms"
        case "99.9 ms":
            return f"{seconds * 1e3:#.1f} ms"
        case "999. ms":
            return f"{seconds * 1e3:#.0f} ms"
        case "9.99 s":
            return f"{seconds:#.2f} s"
        case "99.9 s":
            return f"{seconds:#.1f} s"
        case "999. s":
            return f"{seconds:#.0f} s"
        case "59:59":
            minutes: int
            seconds: int
            seconds = round(seconds)
            minutes, seconds = divmod(seconds, 60)
            return f"{minutes:02d}:{seconds:02d}"
        case "23:59:59":
            hours: int
            minutes: int
            seconds = round(seconds)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        case "1d,23:59:59":
            days: int
            hours: int
            minutes: int
            seconds = round(seconds)
            days, seconds = divmod(seconds, 86400)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            return f"{days}d,{hours:02d}:{minutes:02d}:{seconds:02d}"
        case _:
            raise MatchError(fmt, "format")
