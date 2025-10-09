from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import List
from typing import Optional

@dataclass
class PromptExecution:
    """ author semantha, this is a generated class do not change manually! """
    arguments: Optional[List[str]] = None

PromptExecutionSchema = class_schema(PromptExecution, base_schema=RestSchema)
