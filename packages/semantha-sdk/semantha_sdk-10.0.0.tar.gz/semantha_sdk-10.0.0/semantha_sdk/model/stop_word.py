from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class StopWord:
    """ author semantha, this is a generated class do not change manually! """
    word: str
    id: Optional[str] = None
    standard: Optional[bool] = None

StopWordSchema = class_schema(StopWord, base_schema=RestSchema)
