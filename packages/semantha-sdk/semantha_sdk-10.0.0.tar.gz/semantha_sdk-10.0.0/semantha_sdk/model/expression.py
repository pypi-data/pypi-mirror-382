from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.condition import Condition
from semantha_sdk.model.condition import ConditionSchema
from typing import List
from typing import Optional
from marshmallow import fields

@dataclass
class Expression:
    """ author semantha, this is a generated class do not change manually! """
    then: Optional[List[Condition]] = None
    iff = fields.Nested(ConditionSchema, data_key="if", required=False)

ExpressionSchema = class_schema(Expression, base_schema=RestSchema)
