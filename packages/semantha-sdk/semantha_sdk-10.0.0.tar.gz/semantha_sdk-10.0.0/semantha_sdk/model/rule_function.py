from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional
from semantha_sdk.model.rule_function_type_enum import RuleFunctionTypeEnum

@dataclass
class RuleFunction:
    """ author semantha, this is a generated class do not change manually! """
    name: Optional[str] = None
    min_arg_length: Optional[int] = None
    max_arg_length: Optional[int] = None
    type: Optional[RuleFunctionTypeEnum] = None

RuleFunctionSchema = class_schema(RuleFunction, base_schema=RestSchema)
