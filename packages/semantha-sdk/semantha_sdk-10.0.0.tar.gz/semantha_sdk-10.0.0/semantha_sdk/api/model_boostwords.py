from semantha_sdk.api.model_boostword import ModelBoostwordEndpoint
from semantha_sdk.model.boost_word import BoostWord
from semantha_sdk.model.boost_word import BoostWordSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelBoostwordsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/boostwords"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/boostwords"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ModelBoostwordEndpoint:
        return ModelBoostwordEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[BoostWord]:
        """
        Read all available entities.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(BoostWordSchema)

    def post(
        self,
        body: BoostWord = None,
    ) -> BoostWord:
        """
        Create a new entity. Needs roles: 'Domain Admin' or 'Expert User'
        Args:
        body (BoostWord): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=BoostWordSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(BoostWordSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all available entities. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    