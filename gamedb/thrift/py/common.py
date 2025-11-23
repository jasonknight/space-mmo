from typing import Any, Dict
from game.ttypes import StatusType, BackingTable
from game.constants import TABLE2STR

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

# Create reverse map from table name strings to BackingTable enum values
STR2TABLE: Dict[str, BackingTable] = {
    table_name: backing_table
    for backing_table, table_name in TABLE2STR.items()
}

