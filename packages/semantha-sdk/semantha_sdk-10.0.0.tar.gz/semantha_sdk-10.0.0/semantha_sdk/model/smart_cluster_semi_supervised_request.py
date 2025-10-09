from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.semi_super_vised_document import SemiSuperVisedDocument
from typing import List
from typing import Optional
from semantha_sdk.model.smart_cluster_semi_supervised_request_clustering_structure_enum import SmartClusterSemiSupervisedRequestClustering_structureEnum
from semantha_sdk.model.smart_cluster_semi_supervised_request_topic_over_time_range_enum import SmartClusterSemiSupervisedRequestTopic_over_time_rangeEnum

@dataclass
class SmartClusterSemiSupervisedRequest:
    """ author semantha, this is a generated class do not change manually! """
    clustering_name: Optional[str] = None
    min_cluster_size: Optional[str] = None
    clustering_structure: Optional[SmartClusterSemiSupervisedRequestClustering_structureEnum] = None
    topic_over_time_range: Optional[SmartClusterSemiSupervisedRequestTopic_over_time_rangeEnum] = None
    reduce_outliers: Optional[bool] = None
    umap_nr_of_neighbors: Optional[int] = None
    documents: Optional[List[SemiSuperVisedDocument]] = None

SmartClusterSemiSupervisedRequestSchema = class_schema(SmartClusterSemiSupervisedRequest, base_schema=RestSchema)
