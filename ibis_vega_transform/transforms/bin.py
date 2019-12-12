from typing import *

import ibis
from mypy_extensions import TypedDict
from typing_extensions import Literal
from ..tracer import tracer

__all__ = ["bin"]

BinTransform = TypedDict(
    "BinTransform",
    {
        # Original field name
        "field": str,
        "type": Literal["bin"],
        # the  name of the columns to store the left and right side of the bin
        "as": Tuple[str, str],
        # The number of bins
        "maxbins": int,
        # field that we should get the extent from
        "extent": str,
    },
)


def bin(transform: BinTransform, expr: ibis.Expr) -> ibis.Expr:
    """
    Apply a vega bin transform to an ibis expression.
    https://vega.github.io/vega/docs/transforms/bin/
    """

    field = expr[transform["field"]]
    as_left, as_right = transform["as"]
    maxbins = transform["maxbins"]
    extent = expr[transform["extent"]]

    # Precompute min/max or else we get
    # "Expression 'xxx' is not being grouped"
    # errors
    with tracer.start_span("bin_transform:min") as span:
        min_expr = extent.min()
        span.log_kv({"sql": min_expr.compile()})
        min_ = min_expr.execute()
    with tracer.start_span("bin_transform:max") as span:
        max_expr = extent.max()
        span.log_kv({"sql": max_expr.compile()})
        max_ = max_expr.execute()

    # Cast these to floats to work around
    # https://github.com/ibis-project/ibis/issues/1934
    binwidth = (max_ - min_) / maxbins

    bin_ = (((field / _float(binwidth)) - _float(min_ / binwidth))).floor()
    left = (min_ + (bin_ * binwidth)).name(as_left)
    right = (((min_ + binwidth) + (bin_ * binwidth))).name(as_right)

    # add the two new fields and remove the initial column
    return expr.mutate(
        [left, right]
        # + [c for c in expr.columns if c not in {transform["field"], as_left, as_right}]
    )


def _float(value) -> ibis.Expr:
    return ibis.literal(value, "float64").cast("float32")
