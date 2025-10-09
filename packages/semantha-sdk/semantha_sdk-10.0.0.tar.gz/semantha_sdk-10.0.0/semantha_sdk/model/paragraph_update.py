from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class ParagraphUpdate:
    """ author semantha, this is a generated class do not change manually! """
    text: Optional[str] = None
    type: Optional[str] = None

ParagraphUpdateSchema = class_schema(ParagraphUpdate, base_schema=RestSchema)
