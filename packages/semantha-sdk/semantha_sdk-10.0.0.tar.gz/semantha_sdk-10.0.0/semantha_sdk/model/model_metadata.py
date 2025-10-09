from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class ModelMetadata:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    type: str
    id: Optional[str] = None
    read_only: Optional[bool] = None

ModelMetadataSchema = class_schema(ModelMetadata, base_schema=RestSchema)
