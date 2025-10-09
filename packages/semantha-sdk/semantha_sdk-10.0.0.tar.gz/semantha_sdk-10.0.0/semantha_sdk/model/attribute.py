from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.label import Label
from semantha_sdk.model.metadata_value import MetadataValue
from typing import List
from typing import Optional
from semantha_sdk.model.attribute_datatype_enum import AttributeDatatypeEnum

@dataclass
class Attribute:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    datatype: AttributeDatatypeEnum
    id: Optional[str] = None
    read_only: Optional[bool] = None
    functional: Optional[bool] = None
    labels: Optional[List[Label]] = None
    metadata: Optional[List[MetadataValue]] = None
    comment: Optional[str] = None
    relevant_for_relation: Optional[bool] = None
    object_property_id: Optional[str] = None

AttributeSchema = class_schema(Attribute, base_schema=RestSchema)
