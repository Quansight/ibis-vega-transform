import ibis


def aggregate(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    groupby, = transform["groupby"]
    ops = transform["ops"]
    fields = transform["fields"]
    as_ = transform["as"]
    expr = expr.group_by(groupby).aggregate(
        [
            getattr(expr[field] if field else expr, _translate_op(op))().name(as__)
            for (field, op, as__) in zip(fields, ops, as_)
        ]
    )
    return expr


def _translate_op(op: str) -> str:
    return {"mean": "mean", "average": "mean", "count": "count"}.get(op, op)
