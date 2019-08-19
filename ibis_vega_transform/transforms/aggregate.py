from typing import *

import ibis
import ibis.expr.types as it


def aggregate(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    """
    Apply a vega aggregate transform to an ibis expression.
    https://vega.github.io/vega/docs/transforms/aggregate/

    Parameters
    ----------
    transform: dict
        A JSON-able dictionary representing the vega transform.
    expr: ibis.Expr
        The expression to which to apply the transform.

    Returns
    -------
    transformed_expr: the transformed expression
    """
    groupby = transform["groupby"]
    # It's undocumented, but an undefined "ops" value defaults to ["count"]'
    # https://github.com/vega/vega/blob/4d10f9da0df0833c90ff259bbd0960f7cb05e3bf/packages/vega-transforms/src/Aggregate.js#L159-L161
    ops = transform.get("ops", ["count"])
    fields = transform.get("fields", [None])
    as_ = transform.get("as", [None])

    expr = expr.group_by(groupby).aggregate(
        [
            _aggregate(expr, field, op, as__)
            for (field, op, as__) in zip(fields, ops, as_)
        ]
    )
    return expr


def _aggregate(
    expr: ibis.Expr, field: str, op: str, name: Optional[str] = None
) -> ibis.Expr:
    """
    Apply an aggregation operation to an expression.

    Parameters
    ----------
    expr: ibis.Expr
        The expr to which to apply the aggregation operation.
    field: str
        The name of the field to aggregate.
    op: str
        The name of the aggregation operation, given by
        https://vega.github.io/vega/docs/transforms/aggregate/#ops
        Not all operations are implemented here.
    name: Optional[str]
        A name for the new aggregated value.
    """
    expr = expr[field] if field else expr
    operation = _translate_op(op)
    if not operation:
        raise ValueError(f"Unsupported op {op}")
    expr = operation(expr)
    return expr.name(name) if name else expr


def _translate_op(op: str):
    """
    Map a vega op (https://vega.github.io/vega/docs/transforms/aggregate/#ops)
    to an ibis expression operation.
    """
    return {
        "count": ibis.expr.api.count,
        "distinct": ibis.expr.api.distinct,
        "sum": ibis.expr.api.sum,
        "mean": ibis.expr.api.mean,
        "average": ibis.expr.api.mean,
        "variance": ibis.expr.api.variance,
        "stdev": ibis.expr.api.std,
        "median": ibis.expr.api.approx_median,
        "min": ibis.expr.api.min,
        "max": ibis.expr.api.max,
    }.get(op)
