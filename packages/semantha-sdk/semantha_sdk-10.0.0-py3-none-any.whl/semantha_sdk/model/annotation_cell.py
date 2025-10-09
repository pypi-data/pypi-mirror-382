from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.features import Features
from semantha_sdk.model.rect import Rect
from typing import Optional

@dataclass
class AnnotationCell:
    """ author semantha, this is a generated class do not change manually! """
    bbox: Optional[Rect] = None
    type: Optional[str] = None
    features: Optional[Features] = None

AnnotationCellSchema = class_schema(AnnotationCell, base_schema=RestSchema)
