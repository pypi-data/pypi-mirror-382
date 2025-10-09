from semantha_sdk.administration.transport import TransportEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class DomainEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/administration/domains/{domainname}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._domainname}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        domainname: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._domainname = domainname
        self.__transport = TransportEndpoint(session, self._endpoint)
    
    @property
    def transport(self) -> TransportEndpoint:
        return self.__transport

    
    
    
    
    