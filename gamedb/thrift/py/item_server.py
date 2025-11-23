#!/usr/bin/env python3
"""
ItemService Thrift Server
Starts a Thrift server for the ItemService
"""

import sys
sys.path.append('../gen-py')

import logging
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from game.ItemService import Processor
from services.item_service import ItemServiceHandler
from db import DB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='ItemService Thrift Server')
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host to bind to (default: localhost)',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9090,
        help='Port to bind to (default: 9090)',
    )
    parser.add_argument(
        '--db-host',
        default='localhost',
        help='Database host (default: localhost)',
    )
    parser.add_argument(
        '--db-user',
        default='admin',
        help='Database user (default: admin)',
    )
    parser.add_argument(
        '--db-password',
        default='minda',
        help='Database password (default: minda)',
    )
    parser.add_argument(
        '--database',
        default='gamedb',
        help='Database name (default: gamedb)',
    )

    args = parser.parse_args()

    # Initialize database
    logger.info(f"Connecting to database at {args.db_host}...")
    db = DB(
        host=args.db_host,
        user=args.db_user,
        password=args.db_password,
    )
    db.connect()
    logger.info("Database connection established")

    # Initialize service handler
    handler = ItemServiceHandler(db, args.database)
    processor = Processor(handler)

    # Create server socket
    transport = TSocket.TServerSocket(host=args.host, port=args.port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    # Create server
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    logger.info(f"ItemService starting on {args.host}:{args.port}")
    logger.info(f"Using database: {args.database}")
    logger.info("Press Ctrl+C to stop")

    try:
        server.serve()
    except KeyboardInterrupt:
        logger.info("Server stopped")
    finally:
        if db.connection:
            db.connection.close()
            logger.info("Database connection closed")


if __name__ == '__main__':
    main()
