from typing import Any

import ibis

from . import transforms
from .util import promote_list

# These submodules register appropriate visitors.

__all__ = ["apply"]


def apply(expr: ibis.Expr, transforms: Any) -> ibis.Expr:
    """Apply transform or transforms to the expression.

    Parameters
    ----------
    expr: ibis.Expr
    transform : list
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

    for t in transforms:
        expr = _delegate_transform(t, expr)
    return expr


def _delegate_transform(transform: dict, expr: ibis.Expr) -> ibis.Expr:
    t = getattr(transforms, transform["type"])
    if t is not None:
        return t(transform, expr)
    else:
        raise NotImplementedError(f"Transform of type {t} is not implemented")
