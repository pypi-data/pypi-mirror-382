from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class InstanceOverview:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    class_name: Optional[str] = None
    class_id: Optional[str] = None

InstanceOverviewSchema = class_schema(InstanceOverview, base_schema=RestSchema)
