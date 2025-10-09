from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional
from semantha_sdk.model.attribute_overview_datatype_enum import AttributeOverviewDatatypeEnum

@dataclass
class AttributeOverview:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    datatype: Optional[AttributeOverviewDatatypeEnum] = None

AttributeOverviewSchema = class_schema(AttributeOverview, base_schema=RestSchema)
