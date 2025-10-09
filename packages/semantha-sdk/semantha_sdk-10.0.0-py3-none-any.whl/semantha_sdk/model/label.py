from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class Label:
    """ author semantha, this is a generated class do not change manually! """
    lang: str
    value: str

LabelSchema = class_schema(Label, base_schema=RestSchema)
