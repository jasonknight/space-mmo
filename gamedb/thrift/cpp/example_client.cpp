/**
 * example_client.cpp
 *
 * Example usage of the inventory library.
 * Demonstrates connecting to the InventoryService and performing operations.
 */

#include "inventory.h"
#include "../gen-cpp/game_types.h"

#include <thrift/protocol/TBinaryProtocol.h>
#include <thrift/transport/TSocket.h>
#include <thrift/transport/TTransportUtils.h>

#include <iostream>
#include <memory>

using namespace apache::thrift;
using namespace apache::thrift::protocol;
using namespace apache::thrift::transport;

void print_results(const std::vector<GameResult>& results) {
    for (const auto& result : results) {
        std::cout << "  Status: " << (int)result.status << std::endl;
        std::cout << "  Message: " << result.message << std::endl;
        if (result.__isset.error_code) {
            std::cout << "  Error Code: " << (int)result.error_code << std::endl;
        }
    }
}

int main(int argc, char** argv) {
    try {
        // Configuration
        std::string host = (argc > 1) ? argv[1] : "localhost";
        int port = (argc > 2) ? std::stoi(argv[2]) : 9090;

        std::cout << "Connecting to InventoryService at " << host << ":" << port << std::endl;

        // Create Thrift transport and protocol
        std::shared_ptr<TTransport> socket(new TSocket(host, port));
        std::shared_ptr<TTransport> transport(new TBufferedTransport(socket));
        std::shared_ptr<TProtocol> protocol(new TBinaryProtocol(transport));

        // Open transport
        transport->open();

        // Create game context (as shared_ptr since it will be shared across operations)
        auto context = std::make_shared<game::GameContext>(protocol);

        std::cout << "Connected successfully!" << std::endl;
        std::cout << std::endl;

        // Example 1: Create a new inventory
        std::cout << "=== Example 1: Create Inventory ===" << std::endl;

        Inventory new_inventory;
        new_inventory.__set_max_entries(10);
        new_inventory.__set_max_volume(1000.0);
        new_inventory.__set_last_calculated_volume(0.0);

        // Set owner
        Owner owner;
        owner.__set_mobile_id(100);
        new_inventory.__set_owner(owner);

        // Create empty entries vector
        std::vector<InventoryEntry> entries;
        new_inventory.__set_entries(entries);

        std::vector<GameResult> create_results = game::create_inventory(context, new_inventory);

        std::cout << "Create Results:" << std::endl;
        print_results(create_results);

        if (game::is_ok(create_results)) {
            std::cout << "Inventory created with ID: " << new_inventory.id << std::endl;
        } else {
            std::cout << "Failed to create inventory" << std::endl;
            transport->close();
            return 1;
        }
        std::cout << std::endl;

        // Example 2: Load the inventory
        std::cout << "=== Example 2: Load Inventory ===" << std::endl;

        Inventory loaded_inventory;
        GameResult load_result = game::load_inventory(context, new_inventory.id, loaded_inventory);

        std::cout << "Load Result:" << std::endl;
        std::cout << "  Status: " << (int)load_result.status << std::endl;
        std::cout << "  Message: " << load_result.message << std::endl;

        if (game::is_true(load_result)) {
            std::cout << "Loaded inventory ID: " << loaded_inventory.id << std::endl;
            std::cout << "Max entries: " << loaded_inventory.max_entries << std::endl;
            std::cout << "Max volume: " << loaded_inventory.max_volume << std::endl;
            std::cout << "Number of entries: " << loaded_inventory.entries.size() << std::endl;
        } else {
            std::cout << "Failed to load inventory" << std::endl;
        }
        std::cout << std::endl;

        // Example 3: Update the inventory
        std::cout << "=== Example 3: Save (Update) Inventory ===" << std::endl;

        loaded_inventory.__set_max_entries(20);
        loaded_inventory.__set_max_volume(2000.0);

        std::vector<GameResult> save_results = game::save_inventory(context, loaded_inventory);

        std::cout << "Save Results:" << std::endl;
        print_results(save_results);

        if (game::is_ok(save_results)) {
            std::cout << "Inventory updated successfully" << std::endl;
        } else {
            std::cout << "Failed to update inventory" << std::endl;
        }
        std::cout << std::endl;

        // Example 4: Demonstrate split_stack (requires an item in the inventory)
        // Note: This is just to show the API - it would fail if there are no items
        std::cout << "=== Example 4: Split Stack (API Demo) ===" << std::endl;
        std::cout << "Note: This would require an item in the inventory to work" << std::endl;

        /*
        Inventory split_inventory;
        std::vector<GameResult> split_results = game::split_stack(
            context,
            new_inventory.id,
            1,  // item_id (would need a real item)
            50.0,  // quantity_to_split
            split_inventory
        );

        if (game::is_ok(split_results)) {
            std::cout << "Stack split successfully" << std::endl;
            std::cout << "Inventory now has " << split_inventory.entries.size() << " entries" << std::endl;
        }
        */
        std::cout << "  (Skipped - no items in inventory)" << std::endl;
        std::cout << std::endl;

        // Example 5: Demonstrate transfer_item (requires two inventories with items)
        std::cout << "=== Example 5: Transfer Item (API Demo) ===" << std::endl;
        std::cout << "Note: This would require items in the source inventory to work" << std::endl;

        /*
        Inventory source_inv, dest_inv;
        std::vector<GameResult> transfer_results = game::transfer_item(
            context,
            source_inventory_id,
            destination_inventory_id,
            item_id,
            50.0,  // quantity
            source_inv,
            dest_inv
        );

        if (game::is_ok(transfer_results)) {
            std::cout << "Item transferred successfully" << std::endl;
        }
        */
        std::cout << "  (Skipped - no items in inventory)" << std::endl;
        std::cout << std::endl;

        // Clean up
        transport->close();

        std::cout << "=== All examples completed successfully ===" << std::endl;

        return 0;

    } catch (const game::GameClientException& e) {
        std::cerr << "Game client error: " << e.what() << std::endl;
        return 1;
    } catch (const TException& e) {
        std::cerr << "Thrift error: " << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
