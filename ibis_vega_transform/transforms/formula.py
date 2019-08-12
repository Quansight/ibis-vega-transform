import ibis
from ibis_vega_transform.vegaexpr import eval_vegajs


def formula(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    """
    Apply a vega formula transform to an ibis expression.
    https://vega.github.io/vega/docs/transforms/formula/

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
    col = transform["as"]
    calc = transform["expr"]
    new_col = eval_vegajs(calc, expr).name(col)
    return expr.mutate(new_col)
