from semantha_sdk.api.bulkmodelclass_instances import BulkmodelclassInstancesEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class BulkmodelClassEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/model/domains/{domainname}/classes/{classid}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._classid}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        classid: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._classid = classid
        self.__instances = BulkmodelclassInstancesEndpoint(session, self._endpoint)

    @property
    def instances(self) -> BulkmodelclassInstancesEndpoint:
        return self.__instances

    
    
    
    
    