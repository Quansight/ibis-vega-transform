import ibis
from altair_transform.vegaexpr import eval_vegajs


def formula(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    col = transform["as"]
    calc = transform["expr"]
    new_col = eval_vegajs(calc, expr).name(col)
    return expr.mutate(new_col)
