from game.ttypes import *
from typing import Optional


def is_mobile_attribute(attribute):
    if attribute.owner is not None and attribute.owner.mobile_id is not None:
        return True
    return False


def get_attributes_for_mobile(mobile_id: int, attributes: list[Attribute]) -> Optional[list[Attribute]]:
    matching_attributes = []

    for attribute in attributes:
        attribute_matches = (attribute.owner is not None and
                            attribute.owner.mobile_id is not None and
                            attribute.owner.mobile_id == mobile_id)
        if attribute_matches:
            matching_attributes.append(attribute)

    if matching_attributes:
        return matching_attributes
    return None
