from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.field import Field
from typing import List

@dataclass
class RelationCondition:
    """ author semantha, this is a generated class do not change manually! """
    fields: List[Field]

RelationConditionSchema = class_schema(RelationCondition, base_schema=RestSchema)
