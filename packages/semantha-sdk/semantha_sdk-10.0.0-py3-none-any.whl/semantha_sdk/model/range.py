from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.area import Area
from typing import Optional

@dataclass
class Range:
    """ author semantha, this is a generated class do not change manually! """
    rect: Optional[Area] = None
    page: Optional[int] = None

RangeSchema = class_schema(Range, base_schema=RestSchema)
