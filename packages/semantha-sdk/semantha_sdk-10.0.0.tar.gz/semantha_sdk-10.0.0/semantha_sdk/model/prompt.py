from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional
from semantha_sdk.model.prompt_prompt_label_enum import PromptPrompt_labelEnum

@dataclass
class Prompt:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    prompt_label: PromptPrompt_labelEnum
    id: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    temperature: Optional[float] = None
    top_k: Optional[int] = None
    icon_name: Optional[str] = None

PromptSchema = class_schema(Prompt, base_schema=RestSchema)
