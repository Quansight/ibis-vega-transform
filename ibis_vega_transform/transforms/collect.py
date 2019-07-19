import ibis

from ibis_vega_transform.util import promote_list


def collect(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    """
    Apply a vega collect transform to an ibis expression.
    https://vega.github.io/vega/docs/transforms/collect/

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
    fields = promote_list(transform["sort"]["field"])
    orders = promote_list(transform["sort"].get("order", ["ascending"] * len(fields)))
    assert len(fields) == len(orders)

    rules = [
        (field, (True if order == "ascending" else False))
        for field, order in zip(fields, orders)
    ]
    return expr.sort_by(rules)
