from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.source_document import SourceDocument
from typing import Optional

@dataclass
class ClusteredDocument:
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    source_document: Optional[SourceDocument] = None
    probability: Optional[float] = None

ClusteredDocumentSchema = class_schema(ClusteredDocument, base_schema=RestSchema)
