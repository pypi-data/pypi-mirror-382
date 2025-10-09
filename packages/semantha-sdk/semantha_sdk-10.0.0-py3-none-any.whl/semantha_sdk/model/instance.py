from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.instance_child import InstanceChild
from semantha_sdk.model.simple_property import SimpleProperty
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

@dataclass
class Instance:
    """ author semantha, this is a generated class do not change manually! """
    if TYPE_CHECKING:
        from semantha_sdk.model.instance import Instance
    name: str
    class_id: str
    id: Optional[str] = None
    relation_id: Optional[str] = None
    type: Optional[str] = None
    ignore_import: Optional[bool] = None
    simple_properties: Optional[List[SimpleProperty]] = None
    comment: Optional[str] = None
    if TYPE_CHECKING:
        instances: Optional[List[Instance]] = None
    else:
        instances = None
    childs: Optional[List[InstanceChild]] = None

InstanceSchema = class_schema(Instance, base_schema=RestSchema)
