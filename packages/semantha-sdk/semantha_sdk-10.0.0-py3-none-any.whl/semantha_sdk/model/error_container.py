from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.error_field import ErrorField
from typing import List
from typing import Optional

@dataclass
class ErrorContainer:
    """ author semantha, this is a generated class do not change manually! """
    errors: Optional[List[ErrorField]] = None

ErrorContainerSchema = class_schema(ErrorContainer, base_schema=RestSchema)
