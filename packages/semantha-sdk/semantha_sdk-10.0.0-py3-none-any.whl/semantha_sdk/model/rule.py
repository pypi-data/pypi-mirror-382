from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.expression import Expression
from typing import List
from typing import Optional

@dataclass
class Rule:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    expression: Expression
    id: Optional[str] = None
    comment: Optional[str] = None
    error: Optional[str] = None
    tags: Optional[List[str]] = None
    backward: Optional[bool] = None

RuleSchema = class_schema(Rule, base_schema=RestSchema)
