from semantha_sdk.model.prompt import Prompt
from semantha_sdk.model.prompt import PromptSchema
from semantha_sdk.model.prompt_execution import PromptExecution
from semantha_sdk.model.prompt_execution import PromptExecutionSchema
from semantha_sdk.model.prompt_response import PromptResponse
from semantha_sdk.model.prompt_response import PromptResponseSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class PromptEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/prompts/{id}"
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
    ) -> Prompt:
        """
        Read one entity.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(PromptSchema)

    def post(
        self,
        body: PromptExecution = None,
    ) -> PromptResponse:
        """
        Executes a saved prompt against the configured generative model.
            The 'id' parameter determines which prompt is executed.
        Args:
        body (PromptExecution): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=PromptExecutionSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(PromptResponseSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete one entity. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: Prompt
    ) -> Prompt:
        """
        Change one entity. Needs roles: 'Domain Admin' or 'Expert User'
        """
        return self._session.put(
            url=self._endpoint,
            json=PromptSchema().dump(body)
        ).execute().to(PromptSchema)
