from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.cell_type import CellType
from semantha_sdk.model.custom_field import CustomField
from semantha_sdk.model.document_type_config import DocumentTypeConfig
from typing import List
from typing import Optional

@dataclass
class DocumentType:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    read_only: bool
    id: Optional[str] = None
    celltypes: Optional[List[CellType]] = None
    config: Optional[DocumentTypeConfig] = None
    custom_fields: Optional[List[CustomField]] = None

DocumentTypeSchema = class_schema(DocumentType, base_schema=RestSchema)
