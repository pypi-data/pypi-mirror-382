from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.document_cluster import DocumentCluster
from semantha_sdk.model.plotly_chart import PlotlyChart
from typing import Dict
from typing import List
from typing import Optional

@dataclass
class ClusteringResponse:
    """ author semantha, this is a generated class do not change manually! """
    clusters: Optional[List[DocumentCluster]] = None
    plotly: Optional[Dict[str, PlotlyChart]] = None

ClusteringResponseSchema = class_schema(ClusteringResponse, base_schema=RestSchema)
