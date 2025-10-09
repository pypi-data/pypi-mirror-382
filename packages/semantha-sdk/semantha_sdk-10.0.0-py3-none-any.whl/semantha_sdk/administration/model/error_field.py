from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class ErrorField:
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[str] = None
    status: Optional[str] = None
    code: Optional[str] = None
    title: Optional[str] = None
    detail: Optional[str] = None

ErrorFieldSchema = class_schema(ErrorField, base_schema=RestSchema)
