from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Dict
from typing import Optional

@dataclass
class Reference:
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    page_number: Optional[int] = None
    paragraph_id: Optional[str] = None
    sentence_id: Optional[str] = None
    similarity: Optional[float] = None
    text: Optional[str] = None
    context: Optional[Dict[str, str]] = None
    data_url_image: Optional[str] = None
    type: Optional[str] = None
    color: Optional[str] = None
    comment: Optional[str] = None

ReferenceSchema = class_schema(Reference, base_schema=RestSchema)
