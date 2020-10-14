import typing
from IPython.core.display import JSON
import ibis
from numpy.lib.function_base import disp
import opentracing
import IPython.display

__all__ = [
    "_expr_map",
    "DATA_NAME_PREFIX",
    "get_fallback",
    "set_fallback",
    "get_active_span",
    "set_active_span",
    "enable_debug",
    "disable_debug",
    "reset_debug",
    "debug",
]


_expr_map: typing.Dict[str, ibis.Expr] = {}

DATA_NAME_PREFIX = "ibis:"


# Whether to fallback to getting the dataset as a pandas dataframe
# and rendering it manually, that way.
FALLBACK = False


def set_fallback(fallback: bool) -> None:
    global FALLBACK
    FALLBACK = fallback


def get_fallback() -> bool:
    return FALLBACK


active_span: typing.Optional[opentracing.Span] = None


def set_active_span(scan: typing.Optional[opentracing.Span]) -> None:
    global active_span
    active_span = scan


def get_active_span() -> typing.Optional[opentracing.Span]:
    return active_span


DEBUG = False

DISPLAY = None
JSON_DISPLAY = None


def reset_debug():
    global JSON_DISPLAY, DISPLAY
    JSON_DISPLAY = IPython.display.JSON({}, root="ibis-vega-transform")
    DISPLAY = IPython.display.display(JSON_DISPLAY, display_id=True)


def enable_debug():
    global DEBUG
    DEBUG = True


def disable_debug():
    global DEBUG
    DEBUG = False


def debug(key: str, value):
    if DEBUG:
        JSON_DISPLAY.data[key] = value
        DISPLAY.update(JSON_DISPLAY)
