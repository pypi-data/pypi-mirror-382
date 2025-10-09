from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class InstanceChild:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    relation_id: str
    class_id: str
    id: Optional[str] = None
    class_name: Optional[str] = None

InstanceChildSchema = class_schema(InstanceChild, base_schema=RestSchema)
