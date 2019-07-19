import ibis
from ibis_vega_transform.vegaexpr import eval_vegajs


def filter(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    """
    Apply a vega filter transform to an ibis expression.
    https://vega.github.io/vega/docs/transforms/filter/

    This transform evaluates a vega expression, which is not fully
    implemented. Not every expression will work.

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
    calc = transform["expr"]
    test = eval_vegajs(calc, expr)
    if test is True:
        return expr
    return expr[test]
