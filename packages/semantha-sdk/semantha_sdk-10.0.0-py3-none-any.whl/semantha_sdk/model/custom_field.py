from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class CustomField:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    value: str
    type: str

CustomFieldSchema = class_schema(CustomField, base_schema=RestSchema)
