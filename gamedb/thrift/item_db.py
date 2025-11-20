import sys
import glob
from typing import Optional, Any
sys.path.append('gen-py')

from game.ttypes import *

from thrift import Thrift

CONFIG = ItemDb(
    items=[],
)

CURRENT_ITEM_ID = 1000
CURRENT_ITEM_ATTRIBUTE_ID = 1000

def next_item_id() -> int:
    global CURRENT_ITEM_ID
    CURRENT_ITEM_ID += 1
    return CURRENT_ITEM_ID

def next_item_attribute_id() -> int:
    global CURRENT_ITEM_ATTRIBUTE_ID 
    CURRENT_ITEM_ATTRIBUTE_ID += 1
    return CURRENT_ITEM_ATTRIBUTE_ID



class ItemBuilder:
    def __init__(self, internal_name: str, item_type: ItemType) -> None:
        self.internal_name = internal_name
        self.item_type = item_type
        self.attributes = {}
        self.id = next_item_id()
        self.blueprint = None
        self.max_stack_size = None
    
    def add_item_to_blueprint(self, otheritem: "ItemBuilder", ratio: float) -> "ItemBuilder":
        if self.blueprint is None:
            self.blueprint = ItemBlueprint(
                bake_time_ms=3000,
                components={},
            )
        self.blueprint.components[otheritem.id] = ItemBlueprintComponent(
            item_id=otheritem.id,
            ratio=ratio,
        )
        return self
    
    def add_attribute(
        self, 
        item_attribute_type: AttributeType, 
        internal_name: str, 
        value: Optional[AttributeValue] = None, 
        visible: bool = True
    ) -> "ItemBuilder":
        if value is None:
            value = AttributeValue(
                double_value=0.0
            )
        self.attributes[item_attribute_type] = Attribute(
            id=next_item_attribute_id(),
            internal_name=internal_name,
            visible=visible,
            value=value,
            attribute_type=item_attribute_type
        )
        return self
    
    def stackable_up_to(self, n: int) -> "ItemBuilder":
        self.max_stack_size = n
        return self

    def not_stackable(self) -> "ItemBuilder":
        self.max_stack_size = None
        return self
    
    def build(self) -> Item:     
        return Item(
            id=self.id,
            internal_name=self.internal_name,
            max_stack_size=self.max_stack_size,
            item_type=self.item_type,
            attributes=self.attributes,
            blueprint=self.blueprint,
        )

def attribute_value(bool_value: Optional[bool] = None, double_value: Optional[float] = None) -> AttributeValue:
    if bool_value is not None:
        return AttributeValue(
            bool_value=bool_value,
        )
    if double_value is not None:
        return AttributeValue(
            double_value=double_value,
        )
    raise Exception("Unhandled value")

refined_metallic_materials = {
    "gold": ["calaverite"], 
    "silver": ["argentite","proustite"], 
    "copper": ["chacopyrite", "chalcocite", "bornite", "pyrite"], 
    "iron": ["hematite", "magnetite", "goethite", "siderite"], 
    "manganese": ["pyrolusite", "psilomelane"], 
    "aluminium": ["bauxite", "gibbsite", "boehmite", "diaspore"],
    "zinc": ["sphalerite", "zincite"],
    "lead": ["galena", "cerussite"],
    "nickel": ["pentlandite", "garnierite"],
    "chromium": ["chromite"],
}

for metal, sources in refined_metallic_materials.items():
    source_items = []
    item = ItemBuilder(
        internal_name=metal, 
        item_type=ItemType.REFINEDMATERIAL,
    ).stackable_up_to(10000).add_attribute(
        item_attribute_type=AttributeType.QUANTITY, 
        internal_name="quantity", 
        value=attribute_value(double_value=0.0)
    ).add_attribute(
        item_attribute_type=AttributeType.PURITY, 
        internal_name="purity", 
        value=attribute_value(double_value=0.0)
    ).add_attribute(
        item_attribute_type=AttributeType.VOLUME,
        internal_name="volume",
        value=attribute_value(double_value=1.0),
    )
    for source in sources:
        source_item = ItemBuilder(
            internal_name=source,
            item_type=ItemType.RAWMATERIAL,
        ).add_attribute(
            item_attribute_type=AttributeType.QUANTITY, 
            internal_name="quantity", 
            value=attribute_value(double_value=0.0)
        ).add_attribute(
            item_attribute_type=AttributeType.PURITY, 
            internal_name="purity", 
            value=attribute_value(double_value=0.0)
        ).stackable_up_to(10000).add_attribute(
            item_attribute_type=AttributeType.VOLUME,
            internal_name="volume",
            value=attribute_value(double_value=2.0),
        )
        item.add_item_to_blueprint(source_item, 1.0)
        source_items.append(source_item)

    CONFIG.items.append(
        item.build()
    )
    for source_item in source_items:
        CONFIG.items.append(source_item.build())

def find_item_by_name(name: str) -> Item:
    global CONFIG
    for item in CONFIG.items:
        if item.internal_name == name:
            return item
    raise Exception(f"Could not find item of name {name}")

CARBON = ItemBuilder(
    internal_name="carbon",
    item_type=ItemType.RAWMATERIAL,
).add_attribute(
    item_attribute_type=AttributeType.QUANTITY, 
    internal_name="quantity", 
    value=attribute_value(double_value=0.0)
).add_attribute(
    item_attribute_type=AttributeType.PURITY, 
    internal_name="purity", 
    value=attribute_value(double_value=0.0)
).add_attribute(
    item_attribute_type=AttributeType.VOLUME, 
    internal_name="volume", 
    value=attribute_value(double_value=1.0)
).stackable_up_to(10000)
CONFIG.items.append(CARBON.build())
STEEL = ItemBuilder(
    internal_name="steel", 
    item_type=ItemType.REFINEDMATERIAL,
).stackable_up_to(100).add_attribute(
    item_attribute_type=AttributeType.QUANTITY, 
    internal_name="quantity", 
    value=attribute_value(double_value=0.0)
).add_attribute(
    item_attribute_type=AttributeType.PURITY, 
    internal_name="purity", 
    value=attribute_value(double_value=0.0)
).add_attribute(
    item_attribute_type=AttributeType.VOLUME, 
    internal_name="volume", 
    value=attribute_value(double_value=3.0)
).add_item_to_blueprint(
    otheritem=find_item_by_name("iron"), 
    ratio=0.9
).add_item_to_blueprint(
    otheritem=find_item_by_name("carbon"),
    ratio=0.10,
)
CONFIG.items.append(STEEL.build())
