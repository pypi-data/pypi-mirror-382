from semantha_sdk.model.chat import Chat
from semantha_sdk.model.chat import ChatSchema
from semantha_sdk.model.chat_response import ChatResponse
from semantha_sdk.model.chat_response import ChatResponseSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ChatEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/chats/{id}"
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

    
    def post(
        self,
        body: Chat = None,
    ) -> ChatResponse:
        """
        Chat with the generative model
            The chat endpoint allows you to interact with the generative model in a conversational manner.
        Args:
        body (Chat): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=ChatSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(ChatResponseSchema)

    
    
    