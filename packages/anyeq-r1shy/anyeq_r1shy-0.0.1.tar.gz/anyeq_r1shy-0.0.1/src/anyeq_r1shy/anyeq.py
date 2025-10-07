from typing import List, Any


def anyeq(x: List[Any], y: Any) -> bool:
    for i in x:
        if i == y:
            return True
    return False
