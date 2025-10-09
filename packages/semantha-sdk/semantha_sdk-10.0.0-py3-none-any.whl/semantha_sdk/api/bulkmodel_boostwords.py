from semantha_sdk.model.boost_word import BoostWord
from semantha_sdk.model.boost_word import BoostWordSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class BulkmodelBoostwordsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/model/domains/{domainname}/boostwords"
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

    
    def post(
        self,
        body: List[BoostWord] = None,
    ) -> None:
        """
        Create one or more boostwords
            This is the quiet version of  'post /api/domains/{domainname}/boostwords'
        Args:
        body (List[BoostWord]): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=BoostWordSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    
    