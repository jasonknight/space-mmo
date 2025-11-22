#!/usr/bin/env python3
"""
Start multiple Thrift servers (InventoryService, ItemService, and PlayerService).
Each service runs in a separate process on different ports.
"""

import sys
sys.path.append('../gen-py')

import signal
import multiprocessing
import logging
from typing import Dict, Any, Callable

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from game.InventoryService import Processor as InventoryProcessor
from game.ItemService import Processor as ItemProcessor
from game.PlayerService import Processor as PlayerProcessor
from services.inventory_service import InventoryServiceHandler
from services.item_service import ItemServiceHandler
from services.player_service import PlayerServiceHandler
from db import DB


class PrefixedFormatter(logging.Formatter):
    """Custom formatter that adds a service name prefix to all log messages."""

    def __init__(self, service_name: str, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.service_name = service_name

    def format(self, record):
        original = super().format(record)
        return f"[{self.service_name}] {original}"


def setup_logging(service_name: str):
    """Configure logging with service name prefix."""
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create new handler with prefix
    handler = logging.StreamHandler(sys.stdout)
    formatter = PrefixedFormatter(
        service_name,
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)


def print_prefixed(service_name: str, message: str):
    """Print a message with service name prefix."""
    print(f"[{service_name}] {message}")
    sys.stdout.flush()


def run_inventory_service(config: Dict[str, Any]):
    """Run the InventoryService in a separate process."""
    service_name = config['name']
    setup_logging(service_name)

    # Initialize database connection
    db = DB(
        host=config['db_host'],
        user=config['db_user'],
        password=config['db_password'],
    )

    # Create handler
    handler = InventoryServiceHandler(
        db=db,
        database=config['database'],
        cache_size=config.get('cache_size', 100),
    )

    # Create processor and server
    processor = InventoryProcessor(handler)
    transport = TSocket.TServerSocket(host=config['host'], port=config['port'])
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    # Print startup banner
    print_prefixed(service_name, "=" * 60)
    print_prefixed(service_name, f"Starting {service_name}...")
    print_prefixed(service_name, f"Host: {config['host']}")
    print_prefixed(service_name, f"Port: {config['port']}")
    print_prefixed(service_name, f"Database: {config['database']}")
    print_prefixed(service_name, f"Cache capacity: {config.get('cache_size', 100)}")
    print_prefixed(service_name, "=" * 60)

    try:
        server.serve()
    except KeyboardInterrupt:
        pass
    finally:
        print_prefixed(service_name, "Shutting down...")
        db.disconnect()


def run_item_service(config: Dict[str, Any]):
    """Run the ItemService in a separate process."""
    service_name = config['name']
    setup_logging(service_name)

    # Initialize database connection
    db = DB(
        host=config['db_host'],
        user=config['db_user'],
        password=config['db_password'],
    )

    # Create handler
    handler = ItemServiceHandler(
        db=db,
        database=config['database'],
    )

    # Create processor and server
    processor = ItemProcessor(handler)
    transport = TSocket.TServerSocket(host=config['host'], port=config['port'])
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    # Print startup banner
    print_prefixed(service_name, "=" * 60)
    print_prefixed(service_name, f"Starting {service_name}...")
    print_prefixed(service_name, f"Host: {config['host']}")
    print_prefixed(service_name, f"Port: {config['port']}")
    print_prefixed(service_name, f"Database: {config['database']}")
    print_prefixed(service_name, "=" * 60)

    try:
        server.serve()
    except KeyboardInterrupt:
        pass
    finally:
        print_prefixed(service_name, "Shutting down...")
        db.disconnect()


def run_player_service(config: Dict[str, Any]):
    """Run the PlayerService in a separate process."""
    service_name = config['name']
    setup_logging(service_name)

    # Initialize database connection
    db = DB(
        host=config['db_host'],
        user=config['db_user'],
        password=config['db_password'],
    )

    # Create handler
    handler = PlayerServiceHandler(
        db=db,
        database=config['database'],
        cache_size=config.get('cache_size', 1000),
    )

    # Create processor and server
    processor = PlayerProcessor(handler)
    transport = TSocket.TServerSocket(host=config['host'], port=config['port'])
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    # Print startup banner
    print_prefixed(service_name, "=" * 60)
    print_prefixed(service_name, f"Starting {service_name}...")
    print_prefixed(service_name, f"Host: {config['host']}")
    print_prefixed(service_name, f"Port: {config['port']}")
    print_prefixed(service_name, f"Database: {config['database']}")
    print_prefixed(service_name, f"Cache capacity: {config.get('cache_size', 1000)}")
    print_prefixed(service_name, "=" * 60)

    try:
        server.serve()
    except KeyboardInterrupt:
        pass
    finally:
        print_prefixed(service_name, "Shutting down...")
        db.disconnect()


# Service configuration - add new services here
SERVICES = [
    {
        'name': 'InventoryService',
        'runner': run_inventory_service,
        'config': {
            'name': 'InventoryService',
            'host': '0.0.0.0',
            'port': 9090,
            'db_host': 'localhost',
            'db_user': 'admin',
            'db_password': 'minda',
            'database': 'gamedb',
            'cache_size': 100,
        },
    },
    {
        'name': 'ItemService',
        'runner': run_item_service,
        'config': {
            'name': 'ItemService',
            'host': '0.0.0.0',
            'port': 9091,
            'db_host': 'localhost',
            'db_user': 'admin',
            'db_password': 'minda',
            'database': 'gamedb',
        },
    },
    {
        'name': 'PlayerService',
        'runner': run_player_service,
        'config': {
            'name': 'PlayerService',
            'host': '0.0.0.0',
            'port': 9092,
            'db_host': 'localhost',
            'db_user': 'admin',
            'db_password': 'minda',
            'database': 'gamedb',
            'cache_size': 1000,
        },
    },
]


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\nReceived interrupt signal. Shutting down all services...")
    sys.stdout.flush()


def main():
    """Start all configured services in separate processes."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    processes = []

    # Start each service in a separate process
    for service_def in SERVICES:
        process = multiprocessing.Process(
            target=service_def['runner'],
            args=(service_def['config'],),
            name=service_def['name'],
        )
        process.start()
        processes.append(process)
        print(f"[Main] Started {service_def['name']} (PID: {process.pid})")

    print(f"\n[Main] All services started. Press Ctrl+C to stop.\n")
    sys.stdout.flush()

    try:
        # Wait for all processes
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure all processes are terminated
        print("[Main] Terminating all service processes...")
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    print(f"[Main] Force killing {process.name}...")
                    process.kill()
                    process.join()

        print("[Main] All services stopped.")


if __name__ == '__main__':
    # Required for multiprocessing on some platforms
    multiprocessing.set_start_method('spawn', force=True)
    main()
