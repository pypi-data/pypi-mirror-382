from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.field import Field
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

@dataclass
class Argument:
    """ author semantha, this is a generated class do not change manually! """
    if TYPE_CHECKING:
        from semantha_sdk.model.condition_value import ConditionValue
    value: Optional[str] = None
    fields: Optional[List[Field]] = None
    if TYPE_CHECKING:
        condition: Optional[ConditionValue] = None
    else:
        condition = None

ArgumentSchema = class_schema(Argument, base_schema=RestSchema)
