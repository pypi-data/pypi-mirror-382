from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.attachment import Attachment
from semantha_sdk.model.entity import Entity
from typing import List
from typing import Optional

@dataclass
class DocumentInformation:
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[str] = None
    filename: Optional[str] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    ignored: Optional[bool] = None
    processed: Optional[bool] = None
    lang: Optional[str] = None
    content: Optional[str] = None
    document_class: Optional[Entity] = None
    derived_tags: Optional[List[str]] = None
    color: Optional[str] = None
    derived_color: Optional[str] = None
    comment: Optional[str] = None
    derived_comment: Optional[str] = None
    content_preview: Optional[str] = None
    mime_type: Optional[str] = None
    attachments: Optional[List[Attachment]] = None
    document_class_id: Optional[str] = None

DocumentInformationSchema = class_schema(DocumentInformation, base_schema=RestSchema)
