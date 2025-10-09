from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.extractor import Extractor
from semantha_sdk.model.extractor_attribute import ExtractorAttribute
from typing import List
from typing import Optional

@dataclass
class ExtractorClass:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    class_id: Optional[str] = None
    matcher: Optional[List[Extractor]] = None
    metadata: Optional[str] = None
    attributes: Optional[List[ExtractorAttribute]] = None
    document_type: Optional[str] = None
    split_document_extractor: Optional[str] = None
    linked_classes: Optional[List[str]] = None

ExtractorClassSchema = class_schema(ExtractorClass, base_schema=RestSchema)
