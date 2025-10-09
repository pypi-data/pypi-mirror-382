from semantha_sdk.api.prompt import PromptEndpoint
from semantha_sdk.model.prompt import Prompt
from semantha_sdk.model.prompt import PromptSchema
from semantha_sdk.model.prompt_overview import PromptOverview
from semantha_sdk.model.prompt_overview import PromptOverviewSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class PromptsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/prompts"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/prompts"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> PromptEndpoint:
        return PromptEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[PromptOverview]:
        """
        Read all available entities.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(PromptOverviewSchema)

    def post(
        self,
        body: Prompt = None,
    ) -> Prompt:
        """
        Create a new entity. Needs roles: 'Domain Admin' or 'Expert User'
        Args:
        body (Prompt): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=PromptSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(PromptSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all available entities. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    