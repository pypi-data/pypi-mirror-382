from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import List
from typing import Optional

@dataclass
class Synonym:
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[str] = None
    word: Optional[str] = None
    regex: Optional[str] = None
    synonym: Optional[str] = None
    tags: Optional[List[str]] = None

SynonymSchema = class_schema(Synonym, base_schema=RestSchema)
