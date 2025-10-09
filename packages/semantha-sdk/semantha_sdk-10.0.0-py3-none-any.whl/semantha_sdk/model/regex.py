from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Regex:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    regex: str
    id: Optional[str] = None

RegexSchema = class_schema(Regex, base_schema=RestSchema)
