from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.extraction_area import ExtractionArea
from typing import Optional

@dataclass
class TableInstance:
    """ author semantha, this is a generated class do not change manually! """
    type: Optional[str] = None
    extraction_area: Optional[ExtractionArea] = None

TableInstanceSchema = class_schema(TableInstance, base_schema=RestSchema)
