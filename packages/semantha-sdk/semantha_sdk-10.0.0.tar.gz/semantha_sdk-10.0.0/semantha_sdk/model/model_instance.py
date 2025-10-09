from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.complex_property import ComplexProperty
from semantha_sdk.model.extraction_reference import ExtractionReference
from semantha_sdk.model.file_reference import FileReference
from semantha_sdk.model.finding import Finding
from semantha_sdk.model.label import Label
from semantha_sdk.model.linked_instance import LinkedInstance
from semantha_sdk.model.metadata import Metadata
from semantha_sdk.model.simple_property import SimpleProperty
from typing import List
from typing import Optional

@dataclass
class ModelInstance:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    class_id: str
    id: Optional[str] = None
    relation_id: Optional[str] = None
    type: Optional[str] = None
    ignore_import: Optional[bool] = None
    simple_properties: Optional[List[SimpleProperty]] = None
    metadata: Optional[List[Metadata]] = None
    qualified_name: Optional[str] = None
    extractor_class_ids: Optional[List[str]] = None
    label: Optional[str] = None
    labels: Optional[List[Label]] = None
    file: Optional[FileReference] = None
    complex_properties: Optional[List[ComplexProperty]] = None
    findings: Optional[List[Finding]] = None
    references: Optional[List[ExtractionReference]] = None
    linked_instances: Optional[List[LinkedInstance]] = None

ModelInstanceSchema = class_schema(ModelInstance, base_schema=RestSchema)
