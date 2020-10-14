import altair
import pandas
from opentracing import tags

from .globals import (
    DATA_NAME_PREFIX,
    _expr_map,
    get_active_span,
    get_fallback,
    set_active_span,
    debug,
)
from .tracer import tracer

__all__ = ["altair_data_transformer"]


def altair_data_transformer(data):
    """
    turn a pandas DF with the Ibis query that made it attached to it into
    a valid Vega Lite data dict. Since this has to be JSON serializiable
    (because of how Altair is set up), we create a unique name and
    save the ibis expression globally with that name so we can pick it up later.
    """
    assert isinstance(data, pandas.DataFrame)
    # If there is no ibis attribute, then reutrn the fallback
    if not hasattr(data, "ibis"):
        return altair.default_data_transformer(data)
    expr = data.ibis

    if get_fallback():
        return altair.default_data_transformer(expr.limit(1000).execute())
    # Start a span during the first data transform
    if not get_active_span():
        set_active_span(tracer.start_span("altair", tags={tags.SERVICE: "kernel"}))

    sql = expr.compile()
    get_active_span().log_kv({"sql:initial": sql})
    debug("sql:initial", {"sql": sql})
    h = str(hash(expr))
    name = f"{DATA_NAME_PREFIX}{h}"
    _expr_map[h] = expr
    return {"name": name}
