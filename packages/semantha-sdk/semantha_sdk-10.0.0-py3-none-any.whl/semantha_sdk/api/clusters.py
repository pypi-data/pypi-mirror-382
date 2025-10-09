from semantha_sdk.model.clusteringstructure_enum import ClusteringstructureEnum
from semantha_sdk.model.range_enum import RangeEnum
from semantha_sdk.model.smart_cluster_response_container import SmartClusterResponseContainer
from semantha_sdk.model.smart_cluster_response_container import SmartClusterResponseContainerSchema
from semantha_sdk.model.smart_cluster_semi_supervised_request import SmartClusterSemiSupervisedRequest
from semantha_sdk.model.smart_cluster_semi_supervised_request import SmartClusterSemiSupervisedRequestSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ClustersEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/referencedocuments/clusters"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/clusters"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
        documentids: str = None,
        name: str = None,
        createdafter: int = None,
        createdbefore: int = None,
        updatedafter: int = None,
        updatedbefore: int = None,
        tags: str = None,
        documentclassids: str = None,
        withoutdocumentclass: bool = None,
        mincharacters: int = None,
        metadata: str = None,
        comment: str = None,
        sourcedoc: bool = None,
        sourcedocumentid: str = None,
        minclustersize: str = None,
        clusteringstructure: ClusteringstructureEnum = None,
        reduceoutliers: bool = None,
        range: RangeEnum = None,
        neighbors: int = None,
    ) -> SmartClusterResponseContainer:
        """
        Clusters reference documents based on their semantic content and provides labels for each cluster
        Args:
        documentids str: List of document Ids for target. The limit here is 65000 IDs. The IDs can be passed as a comma separated string.
    name str: Filter documents for a given name
    createdafter int: Filter for documents which are created after a given UNIX timestamp. The createdafter filter only works when also using the parameters offset and limit.
    createdbefore int: Filter for documents which are created before a given UNIX timestamp. The createdbefore filter only works when also using the parameters offset and limit.
    updatedafter int: Filter for documents which are updated after a given UNIX timestamp. The updatedafter filter only works when also using the parameters offset and limit.
    updatedbefore int: Filter for documents which are updated before a given UNIX timestamp. The updatedbefore filter only works when also using the parameters offset and limit.
    tags str: List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentclassids str: List of documentclass IDs for the target. The limit here is 1000 IDs. The IDs are passed as a comma separated list.
    withoutdocumentclass bool: Filters the returned reference documents to include only documents that are not linked to a documentclass. The parameter is of type boolean and is set to false by default.
    mincharacters int: Filters the returned reference documents to include only documents that have a minimum of characters
    metadata str: Filter documents for part of metadata, casing is ignored.
    comment str: Filter documents for part of comment, casing is ignored.
    sourcedoc bool: If true, then only source documents are returned.
    sourcedocumentid str: Filter documents a specific source document.
    minclustersize str: Determines the size of the cluster, values are LOW, MEDIUM, HIGH
    clusteringstructure ClusteringstructureEnum: Determines how clusters are created, values are LOCAL, BALANCED, GLOBAL
    reduceoutliers bool: Boolean to try to reduce outlier on clustering
    range RangeEnum: Used for topic over time clustering, values are HOURS, DAYS, MONTHS, YEARS
    neighbors int: Number of neighbors
        """
        q_params = {}
        if documentids is not None:
            q_params["documentids"] = documentids
        if name is not None:
            q_params["name"] = name
        if createdafter is not None:
            q_params["createdafter"] = createdafter
        if createdbefore is not None:
            q_params["createdbefore"] = createdbefore
        if updatedafter is not None:
            q_params["updatedafter"] = updatedafter
        if updatedbefore is not None:
            q_params["updatedbefore"] = updatedbefore
        if tags is not None:
            q_params["tags"] = tags
        if documentclassids is not None:
            q_params["documentclassids"] = documentclassids
        if withoutdocumentclass is not None:
            q_params["withoutdocumentclass"] = withoutdocumentclass
        if mincharacters is not None:
            q_params["mincharacters"] = mincharacters
        if metadata is not None:
            q_params["metadata"] = metadata
        if comment is not None:
            q_params["comment"] = comment
        if sourcedoc is not None:
            q_params["sourcedoc"] = sourcedoc
        if sourcedocumentid is not None:
            q_params["sourcedocumentid"] = sourcedocumentid
        if minclustersize is not None:
            q_params["minclustersize"] = minclustersize
        if clusteringstructure is not None:
            q_params["clusteringstructure"] = clusteringstructure
        if reduceoutliers is not None:
            q_params["reduceoutliers"] = reduceoutliers
        if range is not None:
            q_params["range"] = range
        if neighbors is not None:
            q_params["neighbors"] = neighbors
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(SmartClusterResponseContainerSchema)

    
    
    
    def put(
        self,
        body: SmartClusterSemiSupervisedRequest
    ) -> SmartClusterResponseContainer:
        """
        
        """
        return self._session.put(
            url=self._endpoint,
            json=SmartClusterSemiSupervisedRequestSchema().dump(body)
        ).execute().to(SmartClusterResponseContainerSchema)
