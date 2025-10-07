import sys

from loguru import logger


def setup_unraisablehook(level: int | str = "ERROR") -> None:
    def unraisablehook(args: "sys.UnraisableHookArgs", /) -> None:
        if logger is None:  # logger has been cleaned up
            return
        logger.opt(exception=(args.exc_type, args.exc_value, args.exc_traceback)).log(
            level,
            "{err_msg}: {object!r}",
            err_msg=args.err_msg or "Exception ignored in",
            object=args.object,
        )

    sys.unraisablehook = unraisablehook
