from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.answer_reference import AnswerReference
from typing import List
from typing import Optional

@dataclass
class Answer:
    """ author semantha, this is a generated class do not change manually! """
    answer: Optional[str] = None
    references: Optional[List[AnswerReference]] = None
    was_chunked: Optional[bool] = None

AnswerSchema = class_schema(Answer, base_schema=RestSchema)
