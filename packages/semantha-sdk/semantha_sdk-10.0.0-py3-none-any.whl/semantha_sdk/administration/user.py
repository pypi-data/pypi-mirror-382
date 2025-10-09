from semantha_sdk.administration.model.user import User
from semantha_sdk.administration.model.user import UserSchema
from semantha_sdk.administration.model.user_update import UserUpdate
from semantha_sdk.administration.model.user_update import UserUpdateSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class UserEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/administration/users/{id}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._id}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        id: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._id = id

    def get(
        self,
    ) -> User:
        """
        
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(UserSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: UserUpdate
    ) -> User:
        """
        
        """
        return self._session.put(
            url=self._endpoint,
            json=UserUpdateSchema().dump(body)
        ).execute().to(UserSchema)
