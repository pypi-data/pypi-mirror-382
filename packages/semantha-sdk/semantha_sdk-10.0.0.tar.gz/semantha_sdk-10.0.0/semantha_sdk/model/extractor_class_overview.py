from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.extractor import Extractor
from typing import List
from typing import Optional

@dataclass
class ExtractorClassOverview:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    class_id: Optional[str] = None
    matcher: Optional[List[Extractor]] = None
    metadata: Optional[str] = None
    attributes: Optional[List[str]] = None

ExtractorClassOverviewSchema = class_schema(ExtractorClassOverview, base_schema=RestSchema)
