from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Formatter:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    description: Optional[str] = None

FormatterSchema = class_schema(Formatter, base_schema=RestSchema)
