from typing import *

import ibis
from mypy_extensions import TypedDict
from typing_extensions import Literal

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
    min_ = extent.min().execute()
    max_ = extent.max().execute()
    # Case these to floats to work around
    # https://github.com/ibis-project/ibis/issues/1934
    binwidth = _cast_float(max_ - min_) / maxbins

    bin_ = ((field - _cast_float(min_)) / binwidth).floor()
    left = (_cast_float(min_) + (bin_ * binwidth)).name(as_left)
    right = (left + binwidth).name(as_right)

    # raise ''
    # add the two new fields and remove the initial column
    return expr.mutate(
        [left, right]
        # + [c for c in expr.columns if c not in {transform["field"], as_left, as_right}]
    )


def _cast_float(value) -> ibis.Expr:
    return ibis.literal(value, "float64").cast("float32")
