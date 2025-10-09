from semantha_sdk.api.chat import ChatEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ChatsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/chats"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/chats"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ChatEndpoint:
        return ChatEndpoint(self._session, self._endpoint, id)

    
    
    
    
    