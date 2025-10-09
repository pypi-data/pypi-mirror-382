from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class CellType:
    """ author semantha, this is a generated class do not change manually! """
    id: str
    name: str
    color: str
    display_name: str
    hidden: bool

CellTypeSchema = class_schema(CellType, base_schema=RestSchema)
