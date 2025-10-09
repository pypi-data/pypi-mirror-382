from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.annotation_cell import AnnotationCell
from typing import List
from typing import Optional

@dataclass
class AnnotationPage:
    """ author semantha, this is a generated class do not change manually! """
    height: Optional[int] = None
    width: Optional[int] = None
    page_number: Optional[int] = None
    ignore_page: Optional[bool] = None
    cells: Optional[List[AnnotationCell]] = None

AnnotationPageSchema = class_schema(AnnotationPage, base_schema=RestSchema)
