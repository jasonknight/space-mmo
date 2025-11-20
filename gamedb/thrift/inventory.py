import sys
import glob
from typing import Optional, Any
import json
import copy
# import pdb
# pdb.set_trace()
sys.path.append('gen-py')

from game.ttypes import *
from item_db import find_item_by_name
from functools import lru_cache
from thrift.protocol.TJSONProtocol import TSimpleJSONProtocolFactory
from thrift.TSerialization import serialize
from common import is_ok, is_true

def debug_inventory(inventory: Inventory) -> str:
    json_data = serialize(inventory, TSimpleJSONProtocolFactory())
    obj = json.loads(json_data)
    json_formatted_str = json.dumps(obj, indent=4)
    return json_formatted_str

def set_item_quantity(item: Item, quantity: float) -> bool:
    for item_attribute_type, item_attribute in item.attributes.items():
        if item_attribute_type == AttributeType.QUANTITY:
            item_attribute.value.double_value = quantity
            return True
    return False

def get_item_quantity(item: Item) -> float:
    if AttributeType.QUANTITY in item.attributes:
        item_attribute = item.attributes[AttributeType.QUANTITY]
        return item_attribute.value.double_value
    return 0.0

def get_entry_free_quantity(entry: InventoryEntry, item: Item) -> float:
    max_stack = item.max_stack_size
    if max_stack is not None:
        amount_that_can_be_added = max_stack - entry.quantity
        if amount_that_can_be_added <= 0.0:
            entry.is_max_stacked = True
            return 0.0
        return amount_that_can_be_added
    return 0.0

def get_item_volume(item: Item, item_quantity: Optional[float] = None) -> float:
    if item_quantity is None:
        if AttributeType.QUANTITY in item.attributes:
            item_attribute = item.attributes[AttributeType.QUANTITY]
            item_quantity = item_attribute.value.double_value
    if item_quantity is not None:
        if AttributeType.VOLUME in item.attributes:
            item_attribute = item.attributes[AttributeType.VOLUME]
            volume = item_attribute.value.double_value
            return item_quantity * volume
    return 0.0

def is_item_in_inventory(inventory: Inventory, item_id: int, quantity: Optional[float] = None) -> GameResult:
    total_quantity = 0.0
    item_found = False

    for entry in inventory.entries:
        if entry.item_id == item_id:
            item_found = True
            total_quantity += entry.quantity

    if not item_found:
        return GameResult(
            status=StatusType.FAILURE,
            message="item not found in inventory",
            error_code=GameError.INV_ITEM_NOT_FOUND
        )

    if quantity is not None and total_quantity < quantity:
        return GameResult(
            status=StatusType.FAILURE,
            message=f"insufficient quantity: requested {quantity}, available {total_quantity}",
            error_code=GameError.INV_INSUFFICIENT_QUANTITY
        )

    return GameResult(
        status=StatusType.SUCCESS,
        message="item found in inventory",
    )



def _can_add_item_to_inventory(inventory: Inventory, item: Item, item_volume: float) -> GameResult:
    if item.item_type == ItemType.VIRTUAL:
        # We can always add a virtual item as it doesn't count towards
        # the totals of count or volume
        return GameResult(
            status=StatusType.SUCCESS,
            message="virtual items can always be added",
        )
    item_is_in_inventory = is_true(is_item_in_inventory(inventory=inventory, item_id=item.id))
    if not item_is_in_inventory and inventory.max_entries == len(inventory.entries):
        return GameResult(
            status=StatusType.FAILURE,
            message="item is not in inventory, and inventory has reached max items",
            error_code=GameError.INV_MAX_ITEMS_REACHED
        )
    # Now we need to ask, is the item in inventory, but all those items are maxxed, so
    # we cannot add one more because of that...
    if item_is_in_inventory:
        max_stacked_items = [entry.is_max_stacked for entry in inventory.entries]
        if all(max_stacked_items) and inventory.max_entries == len(inventory.entries):
            return GameResult(
                status=StatusType.FAILURE,
                message="item is in inventory, but all entries are max stacked",
                error_code=GameError.INV_ALL_ENTRIES_MAX_STACKED
            )

    new_volume = item_volume + inventory.last_calculated_volume
    if  new_volume > inventory.max_volume:
        return GameResult(
            status=StatusType.FAILURE,
            message=f"the new_volume={new_volume} is too high",
            error_code=GameError.INV_NEW_VOLUME_TOO_HIGH
        )
    return GameResult(
        status=StatusType.SUCCESS,
        message="item can be added",
    )

def add_item_to_inventory(
    inventory: Inventory, 
    item: Item, 
    item_quantity: Optional[float] = None, 
    item_volume: Optional[float] = None
) -> list[GameResult]:
    """
    Adding an item to the inventory is not a trivial operation. We need
    to consider 1 how much of the item can we add? Can we add it to an
    existing stack? Can we add it to multiple stacks?
    Can we do a partial add?

    Let's say you pick up a stack of 500 of one item, but your inventory can
    only accept 250 of that item? Do we add the 250? Do we reject entirely?
    """
    results: list[GameResult] = []
    if item_volume is None:
        item_volume = get_item_volume(item=item, item_quantity=item_quantity)
    can_add_item_result = _can_add_item_to_inventory(inventory=inventory, item=item, item_volume=item_volume)
    if not is_true(can_add_item_result):
        return [
            can_add_item_result,
            GameResult(
                status=StatusType.FAILURE,
                message="cannot add this item to the inventory",
                error_code=GameError.INV_CANNOT_ADD_ITEM
            )
        ]
    if item_quantity is None:
        item_quantity = get_item_quantity(item=item)
    for entry in inventory.entries:
        if entry.item_id == item.id:
            can_add_quantity = get_entry_free_quantity(entry=entry, item=item)
            if can_add_quantity > 0.0:
                if can_add_quantity > item_quantity:
                    entry.quantity += item_quantity
                    inventory.last_calculated_volume = item_volume + inventory.last_calculated_volume
                    results.append(
                        GameResult(
                            status=StatusType.SUCCESS,
                            message="item added to inventory",
                        )
                    )
                    return results
                else:
                    delta = item_quantity - can_add_quantity
                    entry.quantity += can_add_quantity
                    delta_volume = get_item_volume(item=item, item_quantity=can_add_quantity)
                    inventory.last_calculated_volume = delta_volume + inventory.last_calculated_volume
                    item_quantity = delta
                    results.append(
                        GameResult(
                            status=StatusType.SUCCESS,
                            message=f"incremented entry by {can_add_quantity}",
                        )
                    )
            else:
                results.append(
                    GameResult(
                        status=StatusType.SKIP,
                        message=f"can_add_quantity={can_add_quantity} so not doing anything here?",
                    )
                )
    if item_quantity > 0.0:
        while item_quantity > 0.0:
            item_volume = get_item_volume(item=item, item_quantity=item_quantity)
            can_add_item_result = _can_add_item_to_inventory(inventory=inventory, item=item, item_volume=item_volume)
            if is_true(can_add_item_result):
                entry = InventoryEntry(
                    item_id=item.id,
                    quantity=0.0,
                    is_max_stacked=False,
                )
                can_add_quantity = get_entry_free_quantity(entry=entry, item=item)
                if can_add_quantity > item_quantity:
                    can_add_quantity = item_quantity
                else:
                    entry.is_max_stacked = True
                delta = item_quantity - can_add_quantity
                entry.quantity += can_add_quantity
                delta_volume = get_item_volume(item=item, item_quantity=can_add_quantity)
                item_quantity = delta
                inventory.entries.append(
                    entry
                )
                inventory.last_calculated_volume = delta_volume + inventory.last_calculated_volume
                results.append(
                    GameResult(
                        status=StatusType.SUCCESS,
                        message=f"added {can_add_quantity} to inventory",
                    )
                )
            else:
                results.append(
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"failed to add {item_quantity} to inventory",
                        error_code=GameError.INV_FAILED_TO_ADD
                    )
                )
                return results
        return results
    else:
        results.append(
            GameResult(
                status=StatusType.SUCCESS,
                message="nothing? item_quantity is not > 0.0",
            )
        )
        return results

def can_transfer_item(
    from_inventory: Inventory,
    to_inventory: Inventory,
    item: Item,
    item_quantity: Optional[float] = None,
) -> list[GameResult]:
    """
    Check if a transfer_item operation would be successful without actually
    performing the transfer. Returns a list of GameResult objects indicating
    whether the transfer would succeed.
    """
    results: list[GameResult] = []

    # Check if the item exists in the from_inventory
    item_found = False
    available_quantity = 0.0

    for entry in from_inventory.entries:
        if entry.item_id == item.id:
            item_found = True
            available_quantity += entry.quantity

    if not item_found:
        return [
            GameResult(
                status=StatusType.FAILURE,
                message=f"item {item.id} not found in from_inventory",
                error_code=GameError.INV_ITEM_NOT_FOUND
            )
        ]

    # Determine the quantity to transfer
    transfer_quantity = item_quantity if item_quantity is not None else available_quantity

    # Check if there's enough quantity available
    if transfer_quantity > available_quantity:
        return [
            GameResult(
                status=StatusType.FAILURE,
                message=f"insufficient quantity: requested {transfer_quantity}, available {available_quantity}",
                error_code=GameError.INV_INSUFFICIENT_QUANTITY
            )
        ]

    # Check if the to_inventory can accept the item
    item_volume = get_item_volume(item=item, item_quantity=transfer_quantity)
    can_add_result = _can_add_item_to_inventory(inventory=to_inventory, item=item, item_volume=item_volume)

    if not is_true(can_add_result):
        return [
            can_add_result,
            GameResult(
                status=StatusType.FAILURE,
                message=f"to_inventory cannot accept {transfer_quantity} of item {item.id}",
                error_code=GameError.INV_CANNOT_ADD_ITEM
            )
        ]

    # Transfer would be successful
    return [
        GameResult(
            status=StatusType.SUCCESS,
            message=f"transfer of {transfer_quantity} of item {item.id} would be successful",
        )
    ]

def transfer_item(
    from_inventory: Inventory,
    to_inventory: Inventory,
    item: Item,
    item_quantity: Optional[float] = None,
) -> list[GameResult]:
    # First, check if the transfer is possible
    can_transfer_results = can_transfer_item(
        from_inventory=from_inventory,
        to_inventory=to_inventory,
        item=item,
        item_quantity=item_quantity
    )

    # If the transfer check fails, return the failure results
    if not is_ok(can_transfer_results):
        return can_transfer_results

    # Transfer is possible, proceed with the actual transfer
    results: list[GameResult] = []
    new_entries = []
    for entry in from_inventory.entries:
        if entry.item_id == item.id:
            if item_quantity is None:
                item_quantity = entry.quantity
            add_results = add_item_to_inventory(inventory=to_inventory, item=item, item_quantity=item_quantity)
            if is_ok(add_results):
                entry.quantity -= item_quantity
                results.append(
                    GameResult(
                        status=StatusType.SUCCESS,
                        message=f"transferred {item_quantity} of {item.id} to {to_inventory.id}",
                    )
                )
            else:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"failed to transfer {item.id} with quantity {item_quantity}",
                        error_code=GameError.INV_FAILED_TO_TRANSFER
                    )
                ] + add_results
        if entry.quantity > 0.0:
            new_entries.append(entry)
        else:
            results.append(
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"removed {entry.item_id} because it's quantity is 0.0"
                )
            )
    from_inventory.entries = new_entries
    return results

def transfer_item_to_first_available_inventory(
    from_inventory: Inventory,
    to_inventories: list[Inventory],
    item: Item,
    item_quantity: Optional[float] = None,
) -> list[GameResult]:
    """
    Iterates over to_inventories and transfers the item to the first inventory
    that can accept it. Returns the results from the successful transfer, or
    a failure result if no inventory can accept the item.
    """
    for to_inventory in to_inventories:
        can_transfer_results = can_transfer_item(
            from_inventory=from_inventory,
            to_inventory=to_inventory,
            item=item,
            item_quantity=item_quantity
        )

        if is_ok(can_transfer_results):
            # Found an inventory that can accept the item
            return transfer_item(
                from_inventory=from_inventory,
                to_inventory=to_inventory,
                item=item,
                item_quantity=item_quantity
            )

    # No inventory could accept the item
    return [
        GameResult(
            status=StatusType.FAILURE,
            message="no available inventory could accept the item",
            error_code=GameError.INV_CANNOT_ADD_ITEM
        )
    ]

def split_stack(
    inventory: Inventory, 
    entry_index: int,
    new_quantity: float
) -> list[GameResult]:
    results: list[GameResult] = []
    if entry_index >= len(inventory.entries):
        results.append(
            GameResult(
                status=StatusType.FAILURE,
                message=f"could not find entry {entry_id}",
                error_code=GameError.INV_COULD_NOT_FIND_ENTRY
            )
        )
        return results
    entry = inventory.entries[entry_index]
    if new_quantity >= entry.quantity:
        results.append(
            GameResult(
                status=StatusType.FAILURE,
                message=f"the new_quantity must be less than, and not equal to, the current entry.quantity",
                error_code=GameError.INV_NEW_QUANTITY_INVALID
            )
        )
        return results
    if len(inventory.entries) >= inventory.max_entries:
        results.append(
            GameResult(
                status=StatusType.FAILURE,
                message=f"inventory is full, cannot split entry",
                error_code=GameError.INV_FULL_CANNOT_SPLIT
            )
        )
        return results
    new_entry = copy.deepcopy(entry)
    entry.quantity -= new_quantity
    new_entry.quantity = new_quantity
    inventory.entries.append(new_entry)
    results.append(
        GameResult(
            status=StatusType.SUCCESS,
            message="split entry",
        )
    )
    return results
    








