from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class LinkedValue:
    """ author semantha, this is a generated class do not change manually! """
    value: Optional[str] = None
    linked_value: Optional[str] = None

LinkedValueSchema = class_schema(LinkedValue, base_schema=RestSchema)
