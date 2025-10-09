from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class SemiSuperVisedDocument:
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    topic_id: Optional[int] = None

SemiSuperVisedDocumentSchema = class_schema(SemiSuperVisedDocument, base_schema=RestSchema)
