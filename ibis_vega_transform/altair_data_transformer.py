import pandas
import typing
import altair

from .tracing import tracer
from .globals import (
    get_fallback,
    DATA_NAME_PREFIX,
    _expr_map,
    get_active_span,
    set_active_span,
)


__all__: typing.List[str] = []


def altair_data_transformer(data):
    """
    turn a pandas DF with the Ibis query that made it attached to it into
    a valid Vega Lite data dict. Since this has to be JSON serializiable
    (because of how Altair is set up), we create a unique name and
    save the ibis expression globally with that name so we can pick it up later.
    """
    assert isinstance(data, pandas.DataFrame)
    expr = data.ibis

    if get_fallback():
        return altair.default_data_transformer(expr.limit(1000).execute())
    # Start a span during the first data transform
    if not get_active_span():
        set_active_span(tracer.start_span("altair"))

    with tracer.start_span("altair_data_transformer", child_of=get_active_span()):
        h = str(hash(expr))
        name = f"{DATA_NAME_PREFIX}{h}"
        _expr_map[h] = expr
        return {"name": name}


altair.data_transformers.register("ibis", altair_data_transformer)
altair.data_transformers.enable("ibis")
