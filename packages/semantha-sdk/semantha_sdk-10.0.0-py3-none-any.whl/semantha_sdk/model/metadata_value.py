from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema


@dataclass
class MetadataValue:
    """ author semantha, this is a generated class do not change manually! """
    id: str
    value: str

MetadataValueSchema = class_schema(MetadataValue, base_schema=RestSchema)
