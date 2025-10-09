from semantha_sdk.api.bulkmodel_domain import BulkmodelDomainEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class BulkmodelDomainsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/model/domains"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/domains"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            domainname: str,
    ) -> BulkmodelDomainEndpoint:
        return BulkmodelDomainEndpoint(self._session, self._endpoint, domainname)

    
    
    
    
    