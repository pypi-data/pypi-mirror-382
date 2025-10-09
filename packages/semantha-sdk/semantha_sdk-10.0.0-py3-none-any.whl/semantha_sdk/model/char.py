from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.rect import Rect
from typing import Optional

@dataclass
class Char:
    """ author semantha, this is a generated class do not change manually! """
    character: str
    area: Optional[Rect] = None

CharSchema = class_schema(Char, base_schema=RestSchema)
