import altair
import opentracing
import typing

from .globals import get_active_span, get_fallback, set_active_span, debug
from .tracer import tracer

__all__ = ["altair_renderer"]

# New Vega Lite renderer mimetype which can process ibis expressions in names
MIMETYPE = "application/vnd.vega.ibis.v5+json"


def altair_renderer(spec):
    """
    An altair renderer that serves our custom mimetype with ibis support.
    """
    active_span = get_active_span()
    # If we don't have an active span, this means we have gone through the data transform
    # on any ibis expressions.s
    if get_fallback() or not active_span:
        return altair.vegalite.v3.display.default_renderer(spec)

    injected_span: typing.Dict = {}
    tracer.inject(active_span, opentracing.Format.TEXT_MAP, injected_span)
    active_span.log_kv({"vega-lite:initial": spec})
    debug("vega-lite:initial", spec)
    active_span.finish()
    set_active_span(None)

    return {MIMETYPE: {"spec": spec, "span": injected_span}}
