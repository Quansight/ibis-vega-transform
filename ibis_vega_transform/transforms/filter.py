import ibis 
from altair_transform.vegaexpr import eval_vegajs

def filter(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    calc = transform['expr']
    return expr.filter(eval_vegajs(calc, expr))
