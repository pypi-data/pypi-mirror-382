from semantha_sdk.api.model_regex import ModelRegexEndpoint
from semantha_sdk.model.regex import Regex
from semantha_sdk.model.regex import RegexSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelRegexesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/regexes"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/regexes"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ModelRegexEndpoint:
        return ModelRegexEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[Regex]:
        """
        Read all available entities.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(RegexSchema)

    def post(
        self,
        body: Regex = None,
    ) -> Regex:
        """
        Create a new entity. Needs roles: 'Domain Admin' or 'Expert User'
        Args:
        body (Regex): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=RegexSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(RegexSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all available entities. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    