from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Any
from typing import List
from typing import Optional

@dataclass
class PlotlyChart:
    """ author semantha, this is a generated class do not change manually! """
    data: Optional[List[Any]] = None
    layout: Optional[Any] = None

PlotlyChartSchema = class_schema(PlotlyChart, base_schema=RestSchema)
