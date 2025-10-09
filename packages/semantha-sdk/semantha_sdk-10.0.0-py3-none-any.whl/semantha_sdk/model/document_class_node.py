from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.custom_field import CustomField
from typing import List
from typing import Optional

@dataclass
class DocumentClassNode:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Optional[str] = None
    documents_count: Optional[int] = None
    custom_fields: Optional[List[CustomField]] = None

DocumentClassNodeSchema = class_schema(DocumentClassNode, base_schema=RestSchema)
