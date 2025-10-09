from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Entity:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None

EntitySchema = class_schema(Entity, base_schema=RestSchema)
