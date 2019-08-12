from typing import *

V = TypeVar("V")


def promote_list(val: Union[V, List[V]]) -> List[V]:
    """
    Maybe wrap a value in a list. If it is already a list, does nothing.
    """
    if not isinstance(val, list):
        val = [val]
    return val
