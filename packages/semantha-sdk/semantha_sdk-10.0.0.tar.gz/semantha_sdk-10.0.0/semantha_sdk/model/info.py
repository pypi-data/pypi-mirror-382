from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class Info:
    """ author semantha, this is a generated class do not change manually! """
    title: str
    vendor: str
    time: str
    git: str
    version: str

InfoSchema = class_schema(Info, base_schema=RestSchema)
