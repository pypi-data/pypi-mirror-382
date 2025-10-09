from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.field import Field
from semantha_sdk.model.relation_condition import RelationCondition
from typing import List
from typing import Optional

@dataclass
class Relation:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    conditions: List[RelationCondition]
    parent: RelationCondition
    id: Optional[str] = None
    source: Optional[List[Field]] = None

RelationSchema = class_schema(Relation, base_schema=RestSchema)
