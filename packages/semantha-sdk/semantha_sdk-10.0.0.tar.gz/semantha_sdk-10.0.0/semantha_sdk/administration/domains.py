from semantha_sdk.administration.domain import DomainEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class DomainsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/administration/domains"
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
    ) -> DomainEndpoint:
        return DomainEndpoint(self._session, self._endpoint, domainname)

    
    
    
    
    