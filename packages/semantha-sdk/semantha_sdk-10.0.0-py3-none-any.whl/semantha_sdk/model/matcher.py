from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Matcher:
    """ author semantha, this is a generated class do not change manually! """
    type: Optional[str] = None
    value: Optional[str] = None

MatcherSchema = class_schema(Matcher, base_schema=RestSchema)
