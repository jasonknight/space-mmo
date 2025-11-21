from typing import Any
from game.ttypes import StatusType

def is_true(result: Any) -> bool:
    if isinstance(result, list):
        for item in result:
            if hasattr(item, "status"):
                if item.status == StatusType.FAILURE:
                    return False
        return True
    if hasattr(result, "status"):
        if result.status != StatusType.FAILURE:
            return True
        else:
            return False
    if isinstance(result, bool):
        return result
    return False

def is_ok(results: list[Any]) -> bool:
    for result in results:
        if hasattr(result, "status"):
            if result.status == StatusType.FAILURE:
                return False
    return True