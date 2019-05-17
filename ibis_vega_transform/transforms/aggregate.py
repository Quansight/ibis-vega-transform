import ibis


def aggregate(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    groupby, = transform["groupby"]
    op, = transform["ops"]
    field, = transform["fields"]
    as_, = transform["as"]
    expr = expr.group_by(groupby).aggregate(
        [getattr(expr[field], _translate_op(op))().name(as_)]
    )
    return expr


def _translate_op(op: str) -> str:
    return {"mean": "mean", "average": "mean"}.get(op, op)
