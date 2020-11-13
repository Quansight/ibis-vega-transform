"""
Functionality for server-side ibis transforms of vega charts.
"""
import json
import re
import typing
import concurrent.futures
import warnings

import ibis.client

try:
    # ibis version >= 1.4
    from ibis.backends import omniscidb as ibis_omniscidb
except ImportError as msg:
    # ibis version < 1.4
    warnings.warn(str(msg))
    from ibis import omniscidb as ibis_omniscidb

import altair
import altair.vegalite.v3.display
import opentracing

from .core import apply
from .globals import _expr_map, debug
from .tracer import tracer

__all__ = ["query_target_func"]

executor = concurrent.futures.ThreadPoolExecutor()


# We need a new connection per thread, which is too memory intensive
# Should just create one per threadpool and then reuse
# But for now we just disable

ENABLE_MULTIPROCESSING = False


def execute_new_client(expr):
    """
    Execute with new connection b/c connections are not threadsafe
    """
    (backend,) = list(ibis.client.find_backends(expr))
    assert isinstance(backend, ibis_omniscidb.OmniSciDBClient)
    with tracer.start_span("ibis:execute:new-client") as execute_span:
        new_client = ibis_omniscidb.OmniSciDBClient(
            uri=backend.uri,
            host=backend.host,
            port=backend.port,
            user=backend.user,
            protocol=backend.protocol,
            session_id=backend.session_id,
            database=backend.db_name,
            password=backend.password,
        )
    with new_client:
        return new_client.execute(expr)

    # reset db name so it reconnects


def query_target_func(comm, msg):
    """
    Target function for actually evaluating the `queryibis` transform.
    """
    # These are the paramaters passed to the vega transform
    parameters: dict = msg["content"]["data"]

    def callback(future):
        comm.send(future.result())

    if ENABLE_MULTIPROCESSING:
        executor.submit(execute_query, parameters).add_done_callback(callback)
    else:
        comm.send(execute_query(parameters))


def execute_query(parameters: dict):
    injected_span: object = parameters.pop("span")
    with tracer.start_active_span(
        "queryibis",
        references=[
            opentracing.child_of(
                (tracer.extract(opentracing.Format.TEXT_MAP, injected_span))
            )
        ],
    ) as scope:
        scope.span.log_kv(parameters)
        name: str = parameters.pop("name")
        transforms: typing.Optional[str] = parameters.pop("transform", None)

        if name not in _expr_map:
            raise ValueError(f"{name} is not an expression known to us!")
        expr = _expr_map[name]
        sql = expr.compile()
        scope.span.log_kv({"sql:initial": sql})
        debug(
            "query:initial",
            {"transforms": transforms, "parameters": parameters, "sql": sql},
        )
        if transforms:
            # Replace all string instances of data references with value in schema
            for k, v in parameters.items():
                # All data items are added to parameters as `:<data name>`.
                # They also should  be in the `data` paramater, but you have to call
                # this with a tuple which I am not sure where to get from
                # https://github.com/vega/vega/blob/65fe7cb2485be90e16298d9dff87bf56045afb8d/packages/vega-transforms/src/Filter.js#L48
                if not k.startswith(":"):
                    continue
                k = k[1:]
                res = json.dumps(v)
                for t in transforms:
                    if t["type"] == "filter" or t["type"] == "formula":
                        t["expr"] = _patch_vegaexpr(t["expr"], k, res)
            try:
                expr = apply(expr, transforms)
            except Exception as e:
                raise ValueError(
                    f"Failed to convert {transforms} with error message message '{e}'"
                )
        with tracer.start_span("ibis:execute") as execute_span:
            sql = expr.compile()
            execute_span.log_kv({"sql": sql})
            if ENABLE_MULTIPROCESSING:
                data = execute_new_client(expr)
            else:
                data = expr.execute()
        values = altair.to_values(data)["values"]
        debug("query:result", {"transforms": transforms, "sql": sql, "values": values})
        return values


def _patch_vegaexpr(expr: str, name: str, value: str) -> str:
    quote = "(['\"])"
    expr = re.sub(f"data\({quote}{name}{quote}\)", value, expr)
    expr = re.sub(
        f"vlSelectionTest\({quote}{name}{quote}", f"vlSelectionTest({value}", expr
    )
    return expr
