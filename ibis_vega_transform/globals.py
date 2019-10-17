import typing
import ibis
import opentracing

__all__ = [
    "_expr_map",
    "DATA_NAME_PREFIX",
    "get_fallback",
    "set_fallback",
    "get_active_span",
    "set_active_span",
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
