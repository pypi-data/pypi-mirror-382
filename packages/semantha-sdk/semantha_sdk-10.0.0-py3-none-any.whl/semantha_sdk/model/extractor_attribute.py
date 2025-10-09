from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.extractor import Extractor
from typing import List
from typing import Optional
from semantha_sdk.model.extractor_attribute_datatype_enum import ExtractorAttributeDatatypeEnum

@dataclass
class ExtractorAttribute:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    property_id: str
    datatype: ExtractorAttributeDatatypeEnum
    default_value: Optional[str] = None
    text_mode: Optional[str] = None
    formatter_id: Optional[str] = None
    text_types: Optional[List[str]] = None
    extract_many: Optional[bool] = None
    extractors: Optional[List[Extractor]] = None

ExtractorAttributeSchema = class_schema(ExtractorAttribute, base_schema=RestSchema)
