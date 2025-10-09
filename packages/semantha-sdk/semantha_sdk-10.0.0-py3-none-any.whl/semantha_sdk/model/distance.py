from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Distance:
    """ author semantha, this is a generated class do not change manually! """
    top: Optional[float] = None
    bottom: Optional[float] = None
    left: Optional[float] = None
    right: Optional[float] = None

DistanceSchema = class_schema(Distance, base_schema=RestSchema)
