/**
 * inventory.h
 *
 * Platform-agnostic C++ client library for game inventory operations.
 * Provides a high-level API that wraps the InventoryService Thrift client.
 *
 * This library is designed to work on both Windows and Linux.
 */

#ifndef INVENTORY_H
#define INVENTORY_H

#include <memory>
#include <vector>
#include <string>
#include <stdexcept>
#include <cstdint>

// Forward declarations for Thrift types
namespace apache { namespace thrift { namespace protocol {
    class TProtocol;
}}}

// Forward declarations for generated types
class InventoryServiceClient;
class GameResult;
class Response;
class Inventory;
class Item;

namespace game {

/**
 * GameContext holds the connection state and Thrift client for inventory operations.
 * The caller is responsible for creating and destroying the context.
 */
class GameContext {
public:
    /**
     * Constructor - creates a context with a Thrift client.
     *
     * @param protocol Shared pointer to Thrift protocol (typically a TBinaryProtocol
     *                 wrapped around a TSocket and TTransport)
     */
    explicit GameContext(std::shared_ptr<apache::thrift::protocol::TProtocol> protocol);

    /**
     * Destructor - cleans up the Thrift client.
     */
    ~GameContext();

    /**
     * Get the underlying InventoryService Thrift client (for advanced usage).
     */
    InventoryServiceClient* getInventoryServiceClient() const;

private:
    std::shared_ptr<InventoryServiceClient> client_;
};

/**
 * Helper function to check if a list of GameResults indicates success.
 *
 * @param results Vector of GameResult objects
 * @return true if all results indicate SUCCESS or SKIP, false otherwise
 */
bool is_ok(const std::vector<GameResult>& results);

/**
 * Helper function to check if a GameResult indicates success.
 *
 * @param result GameResult object
 * @return true if result indicates SUCCESS, false otherwise
 */
bool is_true(const GameResult& result);

/**
 * Load an inventory from the database by ID.
 *
 * @param context Shared pointer to GameContext containing the Thrift client
 * @param inventory_id The ID of the inventory to load
 * @param inventory Output parameter - the loaded inventory (if successful)
 * @return GameResult indicating success or failure
 */
GameResult load_inventory(
    std::shared_ptr<GameContext> context,
    int64_t inventory_id,
    Inventory& inventory
);

/**
 * Create a new inventory in the database.
 *
 * @param context Shared pointer to GameContext containing the Thrift client
 * @param inventory The inventory to create (ID will be set after creation)
 * @return Vector of GameResult objects indicating success or failure
 */
std::vector<GameResult> create_inventory(
    std::shared_ptr<GameContext> context,
    Inventory& inventory
);

/**
 * Save (create or update) an inventory in the database.
 *
 * @param context Shared pointer to GameContext containing the Thrift client
 * @param inventory The inventory to save
 * @return Vector of GameResult objects indicating success or failure
 */
std::vector<GameResult> save_inventory(
    std::shared_ptr<GameContext> context,
    const Inventory& inventory
);

/**
 * Split a stack of items within an inventory.
 *
 * This operation:
 * 1. Loads the inventory from the service
 * 2. Requests the service to split the stack
 * 3. Returns the updated inventory
 *
 * @param context Shared pointer to GameContext containing the Thrift client
 * @param inventory_id The ID of the inventory containing the stack
 * @param item_id The ID of the item to split
 * @param quantity_to_split The quantity to split into a new stack
 * @param updated_inventory Output parameter - the inventory after the split
 * @return Vector of GameResult objects indicating success or failure
 */
std::vector<GameResult> split_stack(
    std::shared_ptr<GameContext> context,
    int64_t inventory_id,
    int64_t item_id,
    double quantity_to_split,
    Inventory& updated_inventory
);

/**
 * Transfer items between two inventories.
 *
 * This operation:
 * 1. Loads both inventories from the service
 * 2. Requests the service to transfer the items
 * 3. Returns both updated inventories
 *
 * @param context Shared pointer to GameContext containing the Thrift client
 * @param source_inventory_id The ID of the source inventory
 * @param destination_inventory_id The ID of the destination inventory
 * @param item_id The ID of the item to transfer
 * @param quantity The quantity to transfer (0 or negative means all available)
 * @param source_inventory Output parameter - the source inventory after transfer
 * @param destination_inventory Output parameter - the destination inventory after transfer
 * @return Vector of GameResult objects indicating success or failure
 */
std::vector<GameResult> transfer_item(
    std::shared_ptr<GameContext> context,
    int64_t source_inventory_id,
    int64_t destination_inventory_id,
    int64_t item_id,
    double quantity,
    Inventory& source_inventory,
    Inventory& destination_inventory
);

/**
 * Exception thrown when a service operation fails.
 */
class GameClientException : public std::runtime_error {
public:
    explicit GameClientException(const std::string& message)
        : std::runtime_error(message) {}
};

} // namespace game

#endif // INVENTORY_H
