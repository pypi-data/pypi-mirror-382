from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class Area:
    """ author semantha, this is a generated class do not change manually! """
    x: float
    y: float
    width: float
    height: float

AreaSchema = class_schema(Area, base_schema=RestSchema)
