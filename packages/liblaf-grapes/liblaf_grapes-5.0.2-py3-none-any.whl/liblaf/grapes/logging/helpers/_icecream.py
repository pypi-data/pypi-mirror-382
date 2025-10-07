from loguru import logger

from liblaf.grapes import pretty

from ._add_level import add_level


def setup_icecream(prefix: str = "") -> None:
    try:
        from icecream import ic
    except ImportError:
        return

    add_level(name="ICECREAM", no=15, color="<magenta><bold>", icon="🍦")

    def output_function(s: str) -> None:
        logger.opt(depth=2).log("ICECREAM", s)

    ic.configureOutput(
        prefix=prefix,
        argToStringFunction=pretty.pformat,
        outputFunction=output_function,
    )
