from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.message import Message
from typing import List
from typing import Optional

@dataclass
class ChatResponse:
    """ author semantha, this is a generated class do not change manually! """
    messages: Optional[List[Message]] = None

ChatResponseSchema = class_schema(ChatResponse, base_schema=RestSchema)
