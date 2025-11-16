import sys
import glob
from typing import Optional, Any
import json
sys.path.append('gen-py')

from game.ttypes import *
from item_db import find_item_by_name
from functools import lru_cache
from thrift.protocol.TJSONProtocol import TSimpleJSONProtocolFactory
from thrift.TSerialization import serialize
player_inventory = Inventory(
    id=1,
    max_items=100,
    max_volume=1000,
    entries=[],
)

def debug_inventory(inventory: Inventory) -> str:
    json_data = serialize(inventory, TSimpleJSONProtocolFactory())
    obj = json.loads(json_data)
    json_formatted_str = json.dumps(obj, indent=4)
    return json_formatted_str

steel_item = find_item_by_name("steel")

def set_item_quantity(item: Item, quantity: float) -> bool:
    for item_attribute_type, item_attribute in item.attributes.items():
        if item_attribute_type == ItemAttributeType.QUANTITY:
            item_attribute.value.double_value = quantity
            return True
    return False


def get_item_quantity(item: Item) -> float:
    if ItemAttributeType.QUANTITY in item.attributes:
        item_attribute = item.attributes[ItemAttributeType.QUANTITY]
        return item_attribute.value.double_value
    return 0.0


def get_item_volume(item: Item) -> float:
    if ItemAttributeType.QUANTITY in item.attributes:
        item_attribute = item.attributes[ItemAttribute.QUANTITY]
        quantity = item_attribute.value.double_value
        if ItemAttributeType.VOLUME in item.attributes:
            item_attribute = item.attributes[ItemAttributeType.VOLUME]
            volume = item_attribute.value.double_value
            return quantity * volume
    return 0.0
def is_item_in_inventory(inventory: Inventory, item_id: int) -> bool:
    for entry in inventory.entries:
        if entry.item_id == item_id:
            return True
    return False

def _can_add_item_to_inventory(inventory: Inventory, item: Item) -> bool:
    if item.item_type == ItemType.VIRTUAL:
        # We can always add a virtual item as it doesn't count towards
        # the totals of count or volume
        return True
    if not is_item_in_inventory(inventory=inventory, item_id=item.id) and inventory.max_items == len(inventory.entries):
        
        return False
    if get_item_volume(item=item) + inventory.last_calculated_volume > inventory.max_volume:
        return False
    return True

def add_item_to_inventory(inventory: Inventory, item: Item) -> bool:
    """
    Adding an item to the inventory is not a trivial operation. We need
    to consider 1 how much of the item can we add? Can we add it to an
    existing stack? Can we add it to multiple stacks?
    Can we do a partial add?

    Let's say you pick up a stack of 500 of one item, but your inventory can
    only accept 250 of that item? Do we add the 250? Do we reject entirely?
    """
    if not _can_add_item_to_inventory(inventory=inventory, item=item):
        return False
    inventory.last_calculated_volume = get_item_volume(item=item) + inventory.last_calculated_volume
    item_quantity = get_item_quantity(item=item)
    for entry in inventory.entries:
        if entry.item_id == item.id:
            entry.quantity += item_quantity
            return True
    inventory.entries.append(
        InventoryEntry(
            item_id=item.id,
            quantity=item_quantity
        )
    )
    return True

set_item_quantity(item=steel_item, quantity=333
                  )
add_item_to_inventory(inventory=player_inventory, item=steel_item)

print(debug_inventory(inventory=player_inventory))

