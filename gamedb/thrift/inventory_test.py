from inventory import *

def test_data():
    player_inventory = Inventory(
        id=1,
        max_entries=5,
        max_volume=1000,
        entries=[],
    )

    player2_inventory = Inventory(
        id=2,
        max_entries=5,
        max_volume=1000,
        entries=[],
    )
    steel_item = find_item_by_name("steel")
    return player_inventory, player2_inventory, steel_item

def reset_inventory_for_test(inventory: Inventory) -> None:
    inventory.entries = []
    inventory.last_calculated_volume = 0.0


def test_item_adding():
    player_inventory, _, steel_item = test_data()
    set_item_quantity(item=steel_item, quantity=320)

    add_item_to_inventory(inventory=player_inventory, item=steel_item)
    assert(len(player_inventory.entries) == 4)

    #print(debug_inventory(inventory=player_inventory))

    results = add_item_to_inventory(inventory=player_inventory, item=steel_item, item_quantity=10.0)
    assert(len(player_inventory.entries) == 4)

    #print(debug_inventory(inventory=player_inventory))

    player_inventory.entries = []
    player_inventory.max_entries = 3
    player_inventory.last_calculated_volume = 0.0

    results = add_item_to_inventory(inventory=player_inventory, item=steel_item)
    # print(results)
    # print(debug_inventory(inventory=player_inventory))
    assert(len(player_inventory.entries) == 3)
    assert(sum([entry.quantity for entry in player_inventory.entries]) == 300)

def test_item_transferring():
    player_inventory, player2_inventory, steel_item = test_data()

    set_item_quantity(item=steel_item, quantity=100)

    add_item_to_inventory(inventory=player_inventory, item=steel_item)

    assert( len(player_inventory.entries) == 1)

    results = transfer_item(
        from_inventory=player_inventory,
        to_inventory=player2_inventory,
        item=steel_item,
        item_quantity=50,
    )

    # print(results)

    assert( len(player_inventory.entries) == 1)
    assert( player_inventory.entries[0].quantity == 50)
    assert( len(player2_inventory.entries) == 1)

    results = transfer_item(
        from_inventory=player_inventory,
        to_inventory=player2_inventory,
        item=steel_item,
        item_quantity=50,
    )

    # print(results)
    # print(debug_inventory(inventory=player_inventory))
    # print(debug_inventory(inventory=player2_inventory))
    assert( len(player_inventory.entries) == 0)
    assert( len(player2_inventory.entries) == 1)

def test_item_splitting():
    """
    So, we want to be able to split items that are stacked.

    Say split item 1 into two stacks of 50 when we have 1 stack of 100

    But there are some caveats.

    What if we are at out item limit? We can't split in that case.

    What if we're asked to split into an amount that's larger than the stack etc?
    """
    player_inventory, _, steel_item = test_data()
    set_item_quantity(item=steel_item, quantity=100)
    add_item_to_inventory(inventory=player_inventory, item=steel_item)
    assert(len(player_inventory.entries) == 1)
    assert(player_inventory.entries[0].quantity == 100)
    split_stack(
        inventory=player_inventory,
        entry_index=0,
        new_quantity=50,
    )
    assert(len(player_inventory.entries) == 2)
    assert(player_inventory.entries[0].quantity == 50)

    # Now test that we can't split when the new_quantity
    # equals the old quantity

    reset_inventory_for_test(inventory=player_inventory)
    add_item_to_inventory(
        inventory=player_inventory,
        item=steel_item,
        item_quantity=1.0,
    )
    assert(player_inventory.entries[0].quantity == 1)
    results = split_stack(
        inventory=player_inventory,
        entry_index=0,
        new_quantity=1.0,
    )
    assert(not is_ok(results))

    # Now test that we can't split with a larger quantity
    # than is available
    reset_inventory_for_test(inventory=player_inventory)
    add_item_to_inventory(
        inventory=player_inventory,
        item=steel_item,
        item_quantity=2.0,
    )
    assert(player_inventory.entries[0].quantity == 2.0)
    results = split_stack(
        inventory=player_inventory,
        entry_index=0,
        new_quantity=3.0,
    )
    assert(not is_ok(results))



def test_transfer_item_to_first_available_inventory():
    """
    Test the transfer_item_to_first_available_inventory function.
    Creates a from_inventory with steel_item quantity 10.
    Creates three to_inventories:
    - First is full due to max_entries
    - Second is full due to max_volume
    - Third is empty and should accept the transfer
    """
    steel_item = find_item_by_name("steel")

    # Create from_inventory with steel_item quantity 10
    from_inventory = Inventory(
        id=1,
        max_entries=5,
        max_volume=1000,
        entries=[],
    )
    add_item_to_inventory(
        inventory=from_inventory,
        item=steel_item,
        item_quantity=10.0
    )
    assert len(from_inventory.entries) == 1
    assert from_inventory.entries[0].quantity == 10.0

    # Create first to_inventory - full because of max_entries
    # We'll set max_entries to 0 so it can't accept any new items
    to_inventory_1 = Inventory(
        id=2,
        max_entries=0,
        max_volume=1000,
        entries=[],
    )

    # Create second to_inventory - full because of max_volume
    # Set max_volume to 0 so it can't accept any items
    to_inventory_2 = Inventory(
        id=3,
        max_entries=5,
        max_volume=0,
        entries=[],
    )

    # Create third to_inventory - empty and can accept items
    to_inventory_3 = Inventory(
        id=4,
        max_entries=5,
        max_volume=1000,
        entries=[],
    )

    to_inventories = [to_inventory_1, to_inventory_2, to_inventory_3]

    # Perform the transfer
    results = transfer_item_to_first_available_inventory(
        from_inventory=from_inventory,
        to_inventories=to_inventories,
        item=steel_item,
        item_quantity=10.0
    )

    # Verify results
    assert is_ok(results), f"Transfer should succeed but got: {results}"

    # Verify the from_inventory is now empty
    assert len(from_inventory.entries) == 0, "from_inventory should be empty after transfer"

    # Verify first two inventories are still empty
    assert len(to_inventory_1.entries) == 0, "First to_inventory should still be empty"
    assert len(to_inventory_2.entries) == 0, "Second to_inventory should still be empty"

    # Verify third inventory received the item
    assert len(to_inventory_3.entries) == 1, "Third to_inventory should have the item"
    assert to_inventory_3.entries[0].quantity == 10.0, "Third to_inventory should have quantity 10"
    assert to_inventory_3.entries[0].item_id == steel_item.id, "Third to_inventory should have steel_item"

test_item_adding()
test_item_transferring()
test_item_splitting()
test_transfer_item_to_first_available_inventory()
