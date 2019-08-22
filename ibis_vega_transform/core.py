from typing import Any

import ibis

from . import transforms
from .util import promote_list

__all__ = ["apply"]


def apply(expr: ibis.Expr, transforms: Any) -> ibis.Expr:
    """Apply transform or transforms to the expression.

    Parameters
    ----------
    expr: ibis.Expr
    transform: list
        A transform specification or list of transform specifications.
        Each specification must be valid according to Vega's transform
        schema.

    Returns
    -------
    expr_transformed : ibis.expr
        The transformed dataframe.
    """
    if transforms is None:
        return expr
    transforms = promote_list(transforms)

    # First traverse list of transforms, and find any that create bins
    # The resulting bin fields, we create as the source fields,
    # Because, for some reason, the filter happens before
    # the binning, but it refers to the field created by the binning
    # See the signals in https://vega.github.io/editor/#/gist/9c7d4dee819450e59cf7381f4d47fee0/example.vl.json
    # as an example
    # TODO: Bring this up with Dominik and see why this is
    for t in transforms:
        if t["type"] == "bin":
            expr = expr.mutate(expr[t["field"]].name(t["as"][0]))

    # Have extra processing for extents that create signals
    # can probably remove once https://github.com/vega/vega-lite/issues/5320 is fixed.
    signal_mapping = {}

    for t in transforms:
        if t["type"] == "extent":
            assert {"field", "signal_", "type"} == t.keys()
            signal_mapping[t["signal_"]] = t["field"]
            continue
        # Change binning that reference  signal extent with actual value
        if "extent" in t and "signal" in t["extent"]:
            t["extent"] = signal_mapping.pop(t["extent"]["signal"])
        expr = _delegate_transform(t, expr)
    return expr


def _delegate_transform(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    """
    Apply a vega transform to an ibis expression.

    Applying this function iteratively to an expression allows the user
    to build up a compound expression out of many vega transforms.

    If a particular transform is not implemented, raises an error.

    Parameters
    ----------
    transform: dict
        A JSON-able representation of a vega transform.
    expr: ibis.Expr
        An expression to transform.

    Returns
    -------
    expr_transformed: The original expression with the additional transform.
    """
    t = getattr(transforms, transform["type"])
    if t is not None:
        return t(transform, expr)
    else:
        raise NotImplementedError(f"Transform of type {t} is not implemented")
