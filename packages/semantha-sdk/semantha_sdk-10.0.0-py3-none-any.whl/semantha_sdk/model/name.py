from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class Name:
    """ author semantha, this is a generated class do not change manually! """
    name: str

NameSchema = class_schema(Name, base_schema=RestSchema)
