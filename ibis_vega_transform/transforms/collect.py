import ibis

from ibis_vega_transform.util import promote_list


def collect(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    fields = promote_list(transform["sort"]["field"])
    orders = promote_list(transform["sort"].get("order", ["ascending"] * len(fields)))
    assert len(fields) == len(orders)

    rules = [
        (field, (True if order == "ascending" else False))
        for field, order in zip(fields, orders)
    ]
    return expr.sort_by(rules)
