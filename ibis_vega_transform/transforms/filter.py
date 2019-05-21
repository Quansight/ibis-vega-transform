import ibis
from ibis_vega_transform.vegaexpr import eval_vegajs


def filter(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    calc = transform["expr"]
    test = eval_vegajs(calc, expr)
    if test is True:
        return expr
    return expr[test]
