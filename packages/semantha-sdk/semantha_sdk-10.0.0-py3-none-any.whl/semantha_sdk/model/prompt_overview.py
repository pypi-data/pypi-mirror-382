from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional
from semantha_sdk.model.prompt_overview_prompt_label_enum import PromptOverviewPrompt_labelEnum

@dataclass
class PromptOverview:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    description: Optional[str] = None
    prompt_label: Optional[PromptOverviewPrompt_labelEnum] = None
    icon_name: Optional[str] = None

PromptOverviewSchema = class_schema(PromptOverview, base_schema=RestSchema)
