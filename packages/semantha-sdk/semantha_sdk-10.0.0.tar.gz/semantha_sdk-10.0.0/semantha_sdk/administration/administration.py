from semantha_sdk.administration.domains import DomainsEndpoint
from semantha_sdk.administration.roles import RolesEndpoint
from semantha_sdk.administration.users import UsersEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class AdministrationEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/administration"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/administration"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self.__domains = DomainsEndpoint(session, self._endpoint)
        self.__roles = RolesEndpoint(session, self._endpoint)
        self.__users = UsersEndpoint(session, self._endpoint)
    
    @property
    def domains(self) -> DomainsEndpoint:
        return self.__domains
    
    @property
    def roles(self) -> RolesEndpoint:
        return self.__roles
    
    @property
    def users(self) -> UsersEndpoint:
        return self.__users

    
    
    
    
    