from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class Metadata:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    value: str

MetadataSchema = class_schema(Metadata, base_schema=RestSchema)
