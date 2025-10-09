from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import List
from typing import Optional
from typing import TYPE_CHECKING

@dataclass
class ModelClass:
    """ author semantha, this is a generated class do not change manually! """
    if TYPE_CHECKING:
        from semantha_sdk.model.model_class import ModelClass
    name: Optional[str] = None
    label: Optional[str] = None
    if TYPE_CHECKING:
        sub_model_classes: Optional[List[ModelClass]] = None
    else:
        sub_model_classes = None

ModelClassSchema = class_schema(ModelClass, base_schema=RestSchema)
