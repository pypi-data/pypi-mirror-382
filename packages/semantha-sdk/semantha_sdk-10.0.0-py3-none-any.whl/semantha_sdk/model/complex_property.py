from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.extraction_area import ExtractionArea
from semantha_sdk.model.extraction_reference import ExtractionReference
from semantha_sdk.model.finding import Finding
from semantha_sdk.model.label import Label
from semantha_sdk.model.metadata import Metadata
from typing import List
from typing import Optional

@dataclass
class ComplexProperty:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    value: str
    label: Optional[str] = None
    id: Optional[str] = None
    class_id: Optional[str] = None
    relation_id: Optional[str] = None
    original_value: Optional[str] = None
    extracted_value: Optional[str] = None
    datatype: Optional[str] = None
    labels: Optional[List[Label]] = None
    metadata: Optional[List[Metadata]] = None
    extraction_area: Optional[ExtractionArea] = None
    findings: Optional[List[Finding]] = None
    references: Optional[List[ExtractionReference]] = None

ComplexPropertySchema = class_schema(ComplexProperty, base_schema=RestSchema)
