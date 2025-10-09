from semantha_sdk.api.model_stopword import ModelStopwordEndpoint
from semantha_sdk.model.stop_word import StopWord
from semantha_sdk.model.stop_word import StopWordSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelStopwordsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/stopwords"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/stopwords"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ModelStopwordEndpoint:
        return ModelStopwordEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[StopWord]:
        """
        Get all stop words
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(StopWordSchema)

    def post(
        self,
        body: StopWord = None,
    ) -> StopWord:
        """
        Create a stop word
        Args:
        body (StopWord): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=StopWordSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(StopWordSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all stop words
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    