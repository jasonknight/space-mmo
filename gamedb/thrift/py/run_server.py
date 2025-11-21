#!/usr/bin/env python3
"""
Start the InventoryService Thrift server.
"""

import sys
sys.path.append('../gen-py')

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from game.InventoryService import Processor
from inventory_service import InventoryServiceHandler
from db import DB

def main():
    # Initialize database connection
    db = DB(
        host="localhost",
        user="admin",
        password="minda",
    )

    # Create handler with cache size
    handler = InventoryServiceHandler(
        db=db,
        database="gamedb",
        cache_size=100,
    )

    # Create processor
    processor = Processor(handler)

    # Setup server
    transport = TSocket.TServerSocket(host='0.0.0.0', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print("=" * 60)
    print("Starting InventoryService server...")
    print(f"Host: 0.0.0.0")
    print(f"Port: 9090")
    print(f"Database: gamedb")
    print(f"Cache capacity: 100")
    print("=" * 60)

    try:
        server.serve()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        db.disconnect()

if __name__ == '__main__':
    main()
