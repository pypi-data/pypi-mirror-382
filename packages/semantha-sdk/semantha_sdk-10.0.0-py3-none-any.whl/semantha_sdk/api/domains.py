from semantha_sdk.api.domain import DomainEndpoint
from semantha_sdk.model.domain_info import DomainInfo
from semantha_sdk.model.domain_info import DomainInfoSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class DomainsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains"
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

    def get(
        self,
    ) -> List[DomainInfo]:
        """
        Returns a list of all accessable domains.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DomainInfoSchema)

    
    
    
    