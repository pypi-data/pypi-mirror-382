from semantha_sdk.api.bulkdomains_domain import BulkdomainsDomainEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class BulkDomainsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/domains"
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
    ) -> BulkdomainsDomainEndpoint:
        return BulkdomainsDomainEndpoint(self._session, self._endpoint, domainname)

    
    
    
    
    