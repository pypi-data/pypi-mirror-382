from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.matcher import Matcher
from semantha_sdk.model.range import Range
from typing import List
from typing import Optional
from semantha_sdk.model.extractor_type_enum import ExtractorTypeEnum
from typing import TYPE_CHECKING

@dataclass
class Extractor:
    """ author semantha, this is a generated class do not change manually! """
    if TYPE_CHECKING:
        from semantha_sdk.model.extractor import Extractor
    type: Optional[ExtractorTypeEnum] = None
    value: Optional[str] = None
    combination_type: Optional[str] = None
    range: Optional[Range] = None
    start: Optional[Matcher] = None
    end: Optional[Matcher] = None
    if TYPE_CHECKING:
        in_between_extractor: Optional[List[Extractor]] = None
    else:
        in_between_extractor = None

ExtractorSchema = class_schema(Extractor, base_schema=RestSchema)
