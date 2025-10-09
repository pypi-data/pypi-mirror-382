from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.label import Label
from typing import List
from typing import Optional

@dataclass
class DataProperty:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    functional: Optional[bool] = None
    labels: Optional[List[Label]] = None

DataPropertySchema = class_schema(DataProperty, base_schema=RestSchema)
