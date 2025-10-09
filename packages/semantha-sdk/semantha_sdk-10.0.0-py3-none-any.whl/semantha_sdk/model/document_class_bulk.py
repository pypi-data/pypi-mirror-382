from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.custom_field import CustomField
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

@dataclass
class DocumentClassBulk:
    """ author semantha, this is a generated class do not change manually! """
    if TYPE_CHECKING:
        from semantha_sdk.model.document_class_bulk import DocumentClassBulk
    name: str
    id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    if TYPE_CHECKING:
        sub_classes: Optional[List[DocumentClassBulk]] = None
    else:
        sub_classes = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None
    comment: Optional[str] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    metadata: Optional[str] = None
    custom_fields: Optional[List[CustomField]] = None

DocumentClassBulkSchema = class_schema(DocumentClassBulk, base_schema=RestSchema)
