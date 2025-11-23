#!/usr/bin/env python3
"""Test PlayerService list_records via Thrift."""

import sys
sys.path.append('../gen-py')

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from game.PlayerService import Client as PlayerServiceClient
from game.ttypes import (
    PlayerRequest,
    PlayerRequestData,
    ListPlayerRequestData,
    StatusType,
)

# Create client
transport = TSocket.TSocket('localhost', 9092)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = PlayerServiceClient(protocol)

try:
    transport.open()
    
    # Make list request
    req = PlayerRequest(
        data=PlayerRequestData(
            list_player=ListPlayerRequestData(
                page=0,
                results_per_page=5,
                search_string=None,
            ),
        ),
    )
    
    resp = client.list_records(req)
    
    if resp.results and resp.results[0].status == StatusType.SUCCESS:
        print(f"✓ Successfully listed players via Thrift service")
        print(f"  Total count: {resp.response_data.list_player.total_count}")
        print()
        
        for player in resp.response_data.list_player.players:
            print(f"Player ID: {player.id}")
            print(f"  Nickname: {player.what_we_call_you}")
            print(f"  Full Name: {player.full_name}")
            
            if hasattr(player, 'mobile') and player.mobile:
                print(f"  Mobile ID: {player.mobile.id}")
                print(f"  Character Name: {player.mobile.what_we_call_you}")
                print("  ✓ Mobile data is present via Thrift!")
            else:
                print("  ✗ Mobile data is MISSING via Thrift!")
            print()
    else:
        error_msg = resp.results[0].message if resp.results else "Unknown error"
        print(f"✗ Failed: {error_msg}")
        
finally:
    transport.close()
