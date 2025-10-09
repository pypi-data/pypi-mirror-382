from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.message import Message
from typing import List
from typing import Optional

@dataclass
class Chat:
    """ author semantha, this is a generated class do not change manually! """
    attributes: Optional[List[str]] = None
    original_prompt_id: Optional[str] = None
    messages: Optional[List[Message]] = None
    temperature: Optional[float] = None
    top_k: Optional[int] = None

ChatSchema = class_schema(Chat, base_schema=RestSchema)
