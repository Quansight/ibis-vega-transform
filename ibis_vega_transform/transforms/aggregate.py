import ibis


def aggregate(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    groupby, = transform["groupby"]
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


def _aggregate(expr, field, op, name):
    expr = expr[field] if field else expr
    expr = getattr(expr, _translate_op(op))()
    return expr.name(name) if name else expr


def _translate_op(op: str) -> str:
    return {"mean": "mean", "average": "mean", "count": "count"}.get(op, op)
