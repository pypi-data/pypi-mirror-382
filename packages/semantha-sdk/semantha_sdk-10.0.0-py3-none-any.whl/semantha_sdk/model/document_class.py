from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.custom_field import CustomField
from semantha_sdk.model.document_class_node import DocumentClassNode
from typing import List
from typing import Optional

@dataclass
class DocumentClass:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Optional[str] = None
    documents_count: Optional[int] = None
    sub_classes: Optional[List[DocumentClassNode]] = None
    custom_fields: Optional[List[CustomField]] = None
    tags: Optional[List[str]] = None
    derived_tags: Optional[List[str]] = None
    color: Optional[str] = None
    derived_color: Optional[str] = None
    comment: Optional[str] = None
    derived_comment: Optional[str] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    derived_metadata: Optional[str] = None

DocumentClassSchema = class_schema(DocumentClass, base_schema=RestSchema)
