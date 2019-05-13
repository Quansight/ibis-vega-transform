from typing import *

V = TypeVar("V")

def promote_list(val: Union[V, List[V]]) -> List[V]:
    if not isinstance(val, list):
        val = [val]
    return val
