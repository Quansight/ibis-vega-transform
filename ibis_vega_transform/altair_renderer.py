import altair
import opentracing
import typing

from .globals import get_active_span, get_fallback, set_active_span
from .tracer import tracer

__all__ = ["altair_renderer"]

# New Vega Lite renderer mimetype which can process ibis expressions in names
MIMETYPE = "application/vnd.vega.ibis.v5+json"


def altair_renderer(spec):
    """
    An altair renderer that serves our custom mimetype with ibis support.
    """
    if get_fallback():
        return altair.vegalite.v3.display.default_renderer(spec)

    active_span = get_active_span()
    assert active_span
    injected_span: typing.Dict = {}
    tracer.inject(active_span, opentracing.Format.TEXT_MAP, injected_span)
    active_span.log_kv({"vega-lite:initial": spec})
    active_span.finish()
    set_active_span(None)

    return {MIMETYPE: {"spec": spec, "span": injected_span}}
