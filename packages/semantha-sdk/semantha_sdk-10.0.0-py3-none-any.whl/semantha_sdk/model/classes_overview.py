from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import List
from typing import Optional
from typing import TYPE_CHECKING

@dataclass
class ClassesOverview:
    """ author semantha, this is a generated class do not change manually! """
    if TYPE_CHECKING:
        from semantha_sdk.model.classes_overview import ClassesOverview
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    if TYPE_CHECKING:
        attributes: Optional[List[ClassesOverview]] = None
    else:
        attributes = None
    object_property_id: Optional[str] = None

ClassesOverviewSchema = class_schema(ClassesOverview, base_schema=RestSchema)
