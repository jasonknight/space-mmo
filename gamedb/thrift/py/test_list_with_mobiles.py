#!/usr/bin/env python3
"""Test that list_player includes mobile data."""

import sys
sys.path.append('../gen-py')

from db import DB
from common import is_ok

# Initialize DB
db = DB(
    host='localhost',
    user='admin',
    password='minda',
)

# Test list_player
print("Testing list_player with mobile data...")
result, players, total_count = db.list_player(
    database='gamedb',
    page=0,
    results_per_page=5,
)

if is_ok([result]):
    print(f"✓ Successfully listed {len(players)} players (total: {total_count})")
    print()
    
    for player in players:
        print(f"Player ID: {player.id}")
        print(f"  Nickname: {player.what_we_call_you}")
        print(f"  Full Name: {player.full_name}")
        
        if hasattr(player, 'mobile') and player.mobile:
            print(f"  Mobile ID: {player.mobile.id}")
            print(f"  Character Name: {player.mobile.what_we_call_you}")
            print("  ✓ Mobile data is present!")
        else:
            print("  ✗ Mobile data is MISSING!")
        print()
else:
    print(f"✗ Failed: {result.message}")
