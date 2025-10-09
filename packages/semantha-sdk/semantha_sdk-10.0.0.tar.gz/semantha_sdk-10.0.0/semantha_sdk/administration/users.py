from semantha_sdk.administration.model.user import User
from semantha_sdk.administration.model.user import UserSchema
from semantha_sdk.administration.model.user_create import UserCreate
from semantha_sdk.administration.model.user_create import UserCreateSchema
from semantha_sdk.administration.user import UserEndpoint
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class UsersEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/administration/users"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/users"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
    def __call__(
            self,
            id: str,
    ) -> UserEndpoint:
        return UserEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[User]:
        """
        
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(UserSchema)

    def post(
        self,
        body: UserCreate = None,
    ) -> User:
        """
        
        Args:
        body (UserCreate): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=UserCreateSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(UserSchema)

    
    
    