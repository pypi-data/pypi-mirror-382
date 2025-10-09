from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.char import Char
from semantha_sdk.model.document_named_entity import DocumentNamedEntity
from semantha_sdk.model.rect import Rect
from semantha_sdk.model.reference import Reference
from typing import List
from typing import Optional

@dataclass
class Sentence:
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[str] = None
    text: Optional[str] = None
    document_name: Optional[str] = None
    named_entities: Optional[List[DocumentNamedEntity]] = None
    references: Optional[List[Reference]] = None
    areas: Optional[List[Rect]] = None
    characters: Optional[List[Char]] = None

SentenceSchema = class_schema(Sentence, base_schema=RestSchema)
