import sys
import glob
import json
sys.path.append('../gen-py')

from game.ttypes import *

from thrift import Thrift
from thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from thrift.protocol.TJSONProtocol import TSimpleJSONProtocolFactory
from thrift.TSerialization import serialize
from item_db import CONFIG
def pretty_print(json_data: str) -> None:
    obj = json.loads(json_data)
    json_formatted_str = json.dumps(obj, indent=4)
    return json_formatted_str
if __name__ == "__main__":
    pretty_formatted = pretty_print(json_data=serialize(CONFIG, TSimpleJSONProtocolFactory()))
    serialized = serialize(CONFIG, TBinaryProtocolFactory())
    print(pretty_formatted)
    with open("./materialized.json", "w+") as f:
        f.write(pretty_formatted)
    with open('./materialized.bin', 'wb+') as f:
        f.write(serialized)