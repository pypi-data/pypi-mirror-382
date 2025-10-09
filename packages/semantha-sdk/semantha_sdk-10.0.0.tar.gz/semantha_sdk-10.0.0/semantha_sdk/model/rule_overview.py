from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import List
from typing import Optional

@dataclass
class RuleOverview:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    rule_string: Optional[str] = None
    tags: Optional[List[str]] = None

RuleOverviewSchema = class_schema(RuleOverview, base_schema=RestSchema)
