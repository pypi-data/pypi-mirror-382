from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.document import Document
from typing import Optional

@dataclass
class ExtractionFile:
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[str] = None
    external_id: Optional[str] = None
    name: Optional[str] = None
    processed: Optional[bool] = None
    binary: Optional[str] = None
    documentextractor: Optional[str] = None
    document: Optional[Document] = None
    filename: Optional[str] = None
    created: Optional[int] = None

ExtractionFileSchema = class_schema(ExtractionFile, base_schema=RestSchema)
