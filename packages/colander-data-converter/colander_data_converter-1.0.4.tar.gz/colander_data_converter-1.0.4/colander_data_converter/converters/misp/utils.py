from typing import Optional, Union

from pymisp import MISPObject, MISPAttribute, MISPEvent


def get_attribute_by_name(misp_object: Union[MISPObject, MISPEvent], name: str) -> Optional[MISPAttribute]:
    for attr in misp_object.attributes:
        if attr.type == name or attr.object_relation == name:
            return attr
    return None
