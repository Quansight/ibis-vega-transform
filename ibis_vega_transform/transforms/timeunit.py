import ibis


def timeunit(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    """
    Apply a vega time unit transform to an ibis expression.
    https://vega.github.io/vega/docs/transforms/timeunit/

    It transforms it into the Ibis truncate expression.
    https://docs.ibis-project.org/generated/ibis.expr.api.TimestampValue.truncate.html

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
    assert transform.pop("type") == "timeunit"
    field = expr[transform.pop("field")]
    as_start, as_end = transform.pop("as")
    units = transform.pop("units")
    if transform:
        raise NotImplementedError(
            f"timeunit transform: {list(transform)} keys are not supported"
        )
    if units == ["year"]:
        start = field.truncate("Y")
        delta = ibis.interval(years=1)
    elif units == ["year", "month"]:
        start = field.truncate("M")
        delta = ibis.interval(months=1)
    elif units == ["year", "month", "date"]:
        start = field.truncate("D")
        delta = ibis.interval(days=1)
    elif units == ["year", "month", "date", "hours"]:
        start = field.truncate("h")
        delta = ibis.interval(hours=1)
    elif units == ["year", "month", "date", "hours", "minutes"]:
        start = field.truncate("m")
        delta = ibis.interval(minutes=1)
    elif units == ["year", "month", "date", "hours", "minutes", "seconds"]:
        start = field.truncate("s")
        delta = ibis.interval(seconds=1)
    elif units == [
        "year",
        "month",
        "date",
        "hours",
        "minutes",
        "seconds",
        "milliseconds",
    ]:
        start = field.truncate("ms")
        delta = ibis.interval(milliseconds=1)
    else:
        raise NotImplementedError(
            f"timeunit transform: {units} units are not supported"
        )
    return expr.mutate([start.name(as_start), (start + delta).name(as_end)])
