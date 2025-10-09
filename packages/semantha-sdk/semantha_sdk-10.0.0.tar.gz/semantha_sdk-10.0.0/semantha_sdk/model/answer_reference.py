from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class AnswerReference:
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[str] = None
    name: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[str] = None

AnswerReferenceSchema = class_schema(AnswerReference, base_schema=RestSchema)
