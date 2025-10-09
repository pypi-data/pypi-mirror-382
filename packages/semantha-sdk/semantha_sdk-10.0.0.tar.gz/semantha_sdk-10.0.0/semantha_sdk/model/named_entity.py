from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class NamedEntity:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    regex: Optional[str] = None

NamedEntitySchema = class_schema(NamedEntity, base_schema=RestSchema)
