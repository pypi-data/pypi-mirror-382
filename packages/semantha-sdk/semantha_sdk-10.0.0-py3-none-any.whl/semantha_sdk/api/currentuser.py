from semantha_sdk.api.roles import RolesEndpoint
from semantha_sdk.model.current_user import CurrentUser
from semantha_sdk.model.current_user import CurrentUserSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class CurrentuserEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/currentuser"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/currentuser"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self.__roles = RolesEndpoint(session, self._endpoint)

    @property
    def roles(self) -> RolesEndpoint:
        return self.__roles

    def get(
        self,
    ) -> CurrentUser:
        """
        Get information about the current user.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(CurrentUserSchema)

    
    
    
    