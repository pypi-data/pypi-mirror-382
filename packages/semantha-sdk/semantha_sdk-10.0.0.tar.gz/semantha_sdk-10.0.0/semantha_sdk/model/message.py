from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional
from semantha_sdk.model.message_role_enum import MessageRoleEnum

@dataclass
class Message:
    """ author semantha, this is a generated class do not change manually! """
    role: Optional[MessageRoleEnum] = None
    content: Optional[str] = None

MessageSchema = class_schema(Message, base_schema=RestSchema)
