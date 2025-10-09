from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class ExtractionReference:
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    similarity: Optional[float] = None
    used: Optional[bool] = None

ExtractionReferenceSchema = class_schema(ExtractionReference, base_schema=RestSchema)
