from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class SourceDocument:
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    paragraph_id: Optional[str] = None

SourceDocumentSchema = class_schema(SourceDocument, base_schema=RestSchema)
