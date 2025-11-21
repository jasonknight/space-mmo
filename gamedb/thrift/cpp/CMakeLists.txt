cmake_minimum_required(VERSION 3.10)
project(GameClient)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Thrift
find_package(Thrift REQUIRED)

# Thrift generated sources directory
set(THRIFT_GEN_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../gen-cpp)

# Thrift generated sources
set(THRIFT_SOURCES
    ${THRIFT_GEN_DIR}/InventoryService.cpp
    ${THRIFT_GEN_DIR}/game_types.cpp
    ${THRIFT_GEN_DIR}/game_constants.cpp
)

# Inventory client library (static)
add_library(inventory STATIC
    inventory.cpp
    ${THRIFT_SOURCES}
)

# Include directories for the library
target_include_directories(inventory PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${THRIFT_GEN_DIR}
    ${THRIFT_INCLUDE_DIRS}
)

# Link Thrift libraries
target_link_libraries(inventory
    ${THRIFT_LIBRARIES}
)

# Platform-specific settings
if(WIN32)
    # Windows-specific settings
    target_compile_definitions(inventory PRIVATE
        _WIN32_WINNT=0x0601
    )
    target_link_libraries(inventory
        ws2_32
    )
elseif(UNIX)
    # Linux-specific settings
    target_link_libraries(inventory
        pthread
    )
endif()

# Example client executable
add_executable(example_client example_client.cpp)
target_link_libraries(example_client inventory)

# Installation rules
install(TARGETS inventory
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)

install(FILES inventory.h
    DESTINATION include
)

# Print configuration info
message(STATUS "GameClient Configuration:")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Thrift Include Dir: ${THRIFT_INCLUDE_DIRS}")
message(STATUS "  Thrift Libraries: ${THRIFT_LIBRARIES}")
message(STATUS "  Generated Thrift Dir: ${THRIFT_GEN_DIR}")
