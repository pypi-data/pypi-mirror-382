from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.file_reference import FileReference
from semantha_sdk.model.rect import Rect
from typing import Optional

@dataclass
class ExtractionArea:
    """ author semantha, this is a generated class do not change manually! """
    file: Optional[FileReference] = None
    rect: Optional[Rect] = None

ExtractionAreaSchema = class_schema(ExtractionArea, base_schema=RestSchema)
