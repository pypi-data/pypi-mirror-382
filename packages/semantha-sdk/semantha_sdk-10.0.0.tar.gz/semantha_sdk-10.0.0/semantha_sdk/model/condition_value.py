from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import List
from typing import Optional
from typing import TYPE_CHECKING

@dataclass
class ConditionValue:
    """ author semantha, this is a generated class do not change manually! """
    if TYPE_CHECKING:
        from semantha_sdk.model.argument import Argument
    function: Optional[str] = None
    if TYPE_CHECKING:
        arguments: Optional[List[Argument]] = None
    else:
        arguments = None

ConditionValueSchema = class_schema(ConditionValue, base_schema=RestSchema)
