import sys
import glob
import json
sys.path.append('../gen-py')

from game.ttypes import *

from thrift import Thrift
from thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from thrift.TSerialization import deserialize

if __name__ == "__main__":
    with open('./materialized.bin', 'rb') as f:
        binary_data = f.read()
        item_db: ItemDb = deserialize(ItemDb(), binary_data,TBinaryProtocolFactory())
        for item in item_db.items:
            
            if item.blueprint is not None:
                print(f"{item.internal_name} {item.blueprint.bake_time_ms}")
                for item_id, component in item.blueprint.components.items():
                    for bp_item in item_db.items:
                        if bp_item.id == item_id:
                            print(f"\t{bp_item.internal_name} {component.ratio}")