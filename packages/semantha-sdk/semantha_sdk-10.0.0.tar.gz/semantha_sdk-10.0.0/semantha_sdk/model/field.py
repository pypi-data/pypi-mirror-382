from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.field_type_enum import FieldTypeEnum

@dataclass
class Field:
    """ author semantha, this is a generated class do not change manually! """
    id: str
    type: FieldTypeEnum

FieldSchema = class_schema(Field, base_schema=RestSchema)
