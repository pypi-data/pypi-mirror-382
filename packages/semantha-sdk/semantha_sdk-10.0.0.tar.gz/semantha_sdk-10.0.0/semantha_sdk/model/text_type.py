from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class TextType:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    color: str
    display_name: str
    hidden: bool

TextTypeSchema = class_schema(TextType, base_schema=RestSchema)
