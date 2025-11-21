/**
 * inventory.cpp
 *
 * Implementation of the game client library.
 */

#include "inventory.h"

// Include generated Thrift types
#include "../gen-cpp/InventoryService.h"
#include "../gen-cpp/game_types.h"

#include <thrift/protocol/TProtocol.h>

namespace game {

// ============================================================================
// GameContext Implementation
// ============================================================================

GameContext::GameContext(std::shared_ptr<apache::thrift::protocol::TProtocol> protocol)
    : client_(std::make_shared<InventoryServiceClient>(protocol))
{
    if (!protocol) {
        throw GameClientException("Protocol cannot be null");
    }
}

GameContext::~GameContext() {
    // Client will be automatically cleaned up by shared_ptr
}

InventoryServiceClient* GameContext::getInventoryServiceClient() const {
    return client_.get();
}

// ============================================================================
// Helper Functions
// ============================================================================

bool is_ok(const std::vector<GameResult>& results) {
    for (const auto& result : results) {
        if (result.status != StatusType::SUCCESS && result.status != StatusType::SKIP) {
            return false;
        }
    }
    return true;
}

bool is_true(const GameResult& result) {
    return result.status == StatusType::SUCCESS;
}

// ============================================================================
// Inventory Operations
// ============================================================================

GameResult load_inventory(
    std::shared_ptr<GameContext> context,
    int64_t inventory_id,
    Inventory& inventory)
{
    try {
        // Create request
        LoadInventoryRequestData load_data;
        load_data.__set_inventory_id(inventory_id);

        RequestData request_data;
        request_data.__set_load_inventory(load_data);

        Request request;
        request.__set_data(request_data);

        // Make RPC call
        Response response;
        context->getInventoryServiceClient()->load(response, request);

        // Check results
        if (!response.results.empty()) {
            const GameResult& result = response.results[0];

            // If successful and we have response data, extract the inventory
            if (is_true(result) && response.__isset.response_data &&
                response.response_data.__isset.load_inventory) {
                inventory = response.response_data.load_inventory.inventory;
            }

            return result;
        }

        // No results returned - create a failure result
        GameResult failure;
        failure.__set_status(StatusType::FAILURE);
        failure.__set_message("No results returned from load operation");
        failure.__set_error_code(GameError::DB_QUERY_FAILED);
        return failure;

    } catch (const std::exception& e) {
        GameResult failure;
        failure.__set_status(StatusType::FAILURE);
        failure.__set_message(std::string("Exception during load: ") + e.what());
        failure.__set_error_code(GameError::DB_QUERY_FAILED);
        return failure;
    }
}

std::vector<GameResult> create_inventory(
    std::shared_ptr<GameContext> context,
    Inventory& inventory)
{
    try {
        // Create request
        CreateInventoryRequestData create_data;
        create_data.__set_inventory(inventory);

        RequestData request_data;
        request_data.__set_create_inventory(create_data);

        Request request;
        request.__set_data(request_data);

        // Make RPC call
        Response response;
        context->getInventoryServiceClient()->create(response, request);

        // Update inventory with created data (including ID)
        if (is_ok(response.results) && response.__isset.response_data &&
            response.response_data.__isset.create_inventory) {
            inventory = response.response_data.create_inventory.inventory;
        }

        return response.results;

    } catch (const std::exception& e) {
        std::vector<GameResult> results;
        GameResult failure;
        failure.__set_status(StatusType::FAILURE);
        failure.__set_message(std::string("Exception during create: ") + e.what());
        failure.__set_error_code(GameError::DB_INSERT_FAILED);
        results.push_back(failure);
        return results;
    }
}

std::vector<GameResult> save_inventory(
    std::shared_ptr<GameContext> context,
    const Inventory& inventory)
{
    try {
        // Create request
        SaveInventoryRequestData save_data;
        save_data.__set_inventory(inventory);

        RequestData request_data;
        request_data.__set_save_inventory(save_data);

        Request request;
        request.__set_data(request_data);

        // Make RPC call
        Response response;
        context->getInventoryServiceClient()->save(response, request);

        return response.results;

    } catch (const std::exception& e) {
        std::vector<GameResult> results;
        GameResult failure;
        failure.__set_status(StatusType::FAILURE);
        failure.__set_message(std::string("Exception during save: ") + e.what());
        failure.__set_error_code(GameError::DB_INSERT_FAILED);
        results.push_back(failure);
        return results;
    }
}

std::vector<GameResult> split_stack(
    std::shared_ptr<GameContext> context,
    int64_t inventory_id,
    int64_t item_id,
    double quantity_to_split,
    Inventory& updated_inventory)
{
    try {
        // Create request
        SplitStackRequestData split_data;
        split_data.__set_inventory_id(inventory_id);
        split_data.__set_item_id(item_id);
        split_data.__set_quantity_to_split(quantity_to_split);

        RequestData request_data;
        request_data.__set_split_stack(split_data);

        Request request;
        request.__set_data(request_data);

        // Make RPC call
        Response response;
        context->getInventoryServiceClient()->split_stack(response, request);

        // Extract updated inventory if successful
        if (is_ok(response.results) && response.__isset.response_data &&
            response.response_data.__isset.split_stack) {
            updated_inventory = response.response_data.split_stack.inventory;
        }

        return response.results;

    } catch (const std::exception& e) {
        std::vector<GameResult> results;
        GameResult failure;
        failure.__set_status(StatusType::FAILURE);
        failure.__set_message(std::string("Exception during split_stack: ") + e.what());
        failure.__set_error_code(GameError::INV_OPERATION_FAILED);
        results.push_back(failure);
        return results;
    }
}

std::vector<GameResult> transfer_item(
    std::shared_ptr<GameContext> context,
    int64_t source_inventory_id,
    int64_t destination_inventory_id,
    int64_t item_id,
    double quantity,
    Inventory& source_inventory,
    Inventory& destination_inventory)
{
    try {
        // Create request
        TransferItemRequestData transfer_data;
        transfer_data.__set_source_inventory_id(source_inventory_id);
        transfer_data.__set_destination_inventory_id(destination_inventory_id);
        transfer_data.__set_item_id(item_id);
        transfer_data.__set_quantity(quantity);

        RequestData request_data;
        request_data.__set_transfer_item(transfer_data);

        Request request;
        request.__set_data(request_data);

        // Make RPC call
        Response response;
        context->getInventoryServiceClient()->transfer_item(response, request);

        // Extract updated inventories if successful
        if (is_ok(response.results) && response.__isset.response_data &&
            response.response_data.__isset.transfer_item) {
            source_inventory = response.response_data.transfer_item.source_inventory;
            destination_inventory = response.response_data.transfer_item.destination_inventory;
        }

        return response.results;

    } catch (const std::exception& e) {
        std::vector<GameResult> results;
        GameResult failure;
        failure.__set_status(StatusType::FAILURE);
        failure.__set_message(std::string("Exception during transfer_item: ") + e.what());
        failure.__set_error_code(GameError::INV_OPERATION_FAILED);
        results.push_back(failure);
        return results;
    }
}

} // namespace game
