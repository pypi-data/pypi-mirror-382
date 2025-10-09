from semantha_sdk.model.stop_word import StopWord
from semantha_sdk.model.stop_word import StopWordSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class BulkmodelStopwordsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/model/domains/{domainname}/stopwords"
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

    
    def post(
        self,
        body: List[StopWord] = None,
    ) -> None:
        """
        Add a list of stop words to your domain
        Args:
        body (List[StopWord]): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=StopWordSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    
    