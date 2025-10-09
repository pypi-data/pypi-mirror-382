from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.distance import Distance
from typing import Optional

@dataclass
class Features:
    """ author semantha, this is a generated class do not change manually! """
    distance: Optional[Distance] = None
    font_size: Optional[int] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    page: Optional[int] = None
    page_rev: Optional[int] = None
    page_width: Optional[float] = None
    page_aspect_ratio: Optional[float] = None
    uppercase: Optional[bool] = None
    starts_with: Optional[str] = None
    contains_text: Optional[bool] = None
    language: Optional[str] = None
    relative_fontsize: Optional[str] = None

FeaturesSchema = class_schema(Features, base_schema=RestSchema)
