# Game Client Library

A platform-agnostic C++ client library for game inventory operations using Apache Thrift.

## Overview

This library provides a high-level API for interacting with the InventoryService. It wraps the Thrift client to provide a clean, intuitive interface for inventory operations such as:

- Loading inventories from the database
- Creating and saving inventories
- Splitting item stacks
- Transferring items between inventories

## Features

- **Platform Agnostic**: Works on both Windows and Linux
- **Minimal Dependencies**: Only requires Apache Thrift
- **Simple API**: Clean wrapper around Thrift RPC calls
- **Context-based**: Uses GameContext for connection management
- **Type-safe**: Uses generated Thrift types for all operations

## Files

- `inventory.h` - Header file with all public API declarations
- `inventory.cpp` - Implementation of the client library
- `example_client.cpp` - Example program demonstrating usage
- `README.md` - This file

## Building

### Prerequisites

- C++11 or later compiler
- Apache Thrift library (libthrift)
- CMake 3.10+ (recommended)

### Linux Build

```bash
# Install Thrift (Ubuntu/Debian)
sudo apt-get install libthrift-dev thrift-compiler

# Compile the library
g++ -std=c++11 -c inventory.cpp -I../gen-cpp -I/usr/include/thrift

# Compile the example
g++ -std=c++11 example_client.cpp inventory.o \
    ../gen-cpp/InventoryService.cpp \
    ../gen-cpp/game_types.cpp \
    ../gen-cpp/game_constants.cpp \
    -I../gen-cpp -I/usr/include/thrift \
    -lthrift -o example_client
```

### Windows Build

```powershell
# Install Thrift (using vcpkg)
vcpkg install thrift

# Compile with MSVC
cl /EHsc /std:c++14 /I..\gen-cpp /I<thrift-include-path> ^
   inventory.cpp ..\gen-cpp\InventoryService.cpp ^
   ..\gen-cpp\game_types.cpp ..\gen-cpp\game_constants.cpp ^
   /link libthrift.lib
```

### CMake Build (Recommended)

Create a `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.10)
project(GameClient)

set(CMAKE_CXX_STANDARD 11)

find_package(Thrift REQUIRED)

# Generated Thrift sources
set(THRIFT_GEN_DIR ${CMAKE_SOURCE_DIR}/../gen-cpp)
set(THRIFT_SOURCES
    ${THRIFT_GEN_DIR}/InventoryService.cpp
    ${THRIFT_GEN_DIR}/game_types.cpp
    ${THRIFT_GEN_DIR}/game_constants.cpp
)

# Game client library
add_library(inventory STATIC
    inventory.cpp
    ${THRIFT_SOURCES}
)

target_include_directories(inventory PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${THRIFT_GEN_DIR}
    ${THRIFT_INCLUDE_DIRS}
)

target_link_libraries(inventory
    ${THRIFT_LIBRARIES}
)

# Example program
add_executable(example_client example_client.cpp)
target_link_libraries(example_client inventory)
```

Then build:

```bash
mkdir build && cd build
cmake ..
make
```

## Usage

### 1. Create a GameContext

The `GameContext` manages the Thrift client connection:

```cpp
#include "inventory.h"
#include <thrift/protocol/TBinaryProtocol.h>
#include <thrift/transport/TSocket.h>
#include <thrift/transport/TTransportUtils.h>

using namespace apache::thrift;
using namespace apache::thrift::protocol;
using namespace apache::thrift::transport;

// Create transport
std::shared_ptr<TTransport> socket(new TSocket("localhost", 9090));
std::shared_ptr<TTransport> transport(new TBufferedTransport(socket));
std::shared_ptr<TProtocol> protocol(new TBinaryProtocol(transport));

// Open connection
transport->open();

// Create game context
game::GameContext context(protocol);
```

### 2. Perform Operations

#### Load Inventory

```cpp
Inventory inventory;
GameResult result = game::load_inventory(context, inventory_id, inventory);

if (game::is_true(result)) {
    std::cout << "Loaded inventory with "
              << inventory.entries.size() << " items" << std::endl;
} else {
    std::cerr << "Failed: " << result.message << std::endl;
}
```

#### Create Inventory

```cpp
Inventory new_inventory;
new_inventory.__set_max_entries(10);
new_inventory.__set_max_volume(1000.0);
new_inventory.__set_entries(std::vector<InventoryEntry>());

Owner owner;
owner.__set_mobile_id(100);
new_inventory.__set_owner(owner);

std::vector<GameResult> results = game::create_inventory(context, new_inventory);

if (game::is_ok(results)) {
    std::cout << "Created inventory ID: " << new_inventory.id << std::endl;
}
```

#### Split Stack

```cpp
Inventory updated_inventory;
std::vector<GameResult> results = game::split_stack(
    context,
    inventory_id,
    item_id,
    50.0,  // quantity to split
    updated_inventory
);

if (game::is_ok(results)) {
    std::cout << "Stack split successfully" << std::endl;
}
```

#### Transfer Item

```cpp
Inventory source_inv, dest_inv;
std::vector<GameResult> results = game::transfer_item(
    context,
    source_inventory_id,
    destination_inventory_id,
    item_id,
    50.0,  // quantity to transfer
    source_inv,
    dest_inv
);

if (game::is_ok(results)) {
    std::cout << "Item transferred successfully" << std::endl;
}
```

### 3. Check Results

Use the helper functions to check operation results:

```cpp
// Check if single result is success
if (game::is_true(result)) {
    // Operation succeeded
}

// Check if all results in a vector are success
if (game::is_ok(results)) {
    // All operations succeeded
}
```

### 4. Clean Up

```cpp
transport->close();
// GameContext destructor will clean up the client
```

## API Reference

### GameContext

```cpp
class GameContext {
public:
    explicit GameContext(std::shared_ptr<apache::thrift::protocol::TProtocol> protocol);
    ~GameContext();
    InventoryServiceClient* getClient() const;
};
```

### Functions

#### load_inventory
```cpp
GameResult load_inventory(
    GameContext& context,
    int64_t inventory_id,
    Inventory& inventory
);
```
Loads an inventory from the database by ID.

#### create_inventory
```cpp
std::vector<GameResult> create_inventory(
    GameContext& context,
    Inventory& inventory
);
```
Creates a new inventory in the database. The inventory's ID will be set after creation.

#### save_inventory
```cpp
std::vector<GameResult> save_inventory(
    GameContext& context,
    const Inventory& inventory
);
```
Saves (creates or updates) an inventory in the database.

#### split_stack
```cpp
std::vector<GameResult> split_stack(
    GameContext& context,
    int64_t inventory_id,
    int64_t item_id,
    double quantity_to_split,
    Inventory& updated_inventory
);
```
Splits a stack of items within an inventory.

#### transfer_item
```cpp
std::vector<GameResult> transfer_item(
    GameContext& context,
    int64_t source_inventory_id,
    int64_t destination_inventory_id,
    int64_t item_id,
    double quantity,
    Inventory& source_inventory,
    Inventory& destination_inventory
);
```
Transfers items between two inventories.

### Helper Functions

```cpp
bool is_ok(const std::vector<GameResult>& results);
bool is_true(const GameResult& result);
```

## Error Handling

All operations return `GameResult` objects that indicate success or failure:

```cpp
struct GameResult {
    StatusType status;        // SUCCESS, FAILURE, or SKIP
    std::string message;      // Human-readable message
    GameError error_code;     // Optional error code
};
```

The library also throws `GameClientException` for critical errors:

```cpp
try {
    game::GameContext context(protocol);
    // ... operations ...
} catch (const game::GameClientException& e) {
    std::cerr << "Client error: " << e.what() << std::endl;
} catch (const TException& e) {
    std::cerr << "Thrift error: " << e.what() << std::endl;
}
```

## Running the Example

1. Start the InventoryService server (Python implementation)
2. Run the example client:

```bash
./example_client localhost 9090
```

## Thread Safety

The `GameContext` and its underlying Thrift client are **not thread-safe**. If you need to make concurrent requests:

1. Create a separate `GameContext` for each thread, or
2. Use mutex locks to synchronize access to a shared context

## License

This library follows the same license as the parent project.

## Support

For issues or questions, refer to the main project documentation or contact the development team.
