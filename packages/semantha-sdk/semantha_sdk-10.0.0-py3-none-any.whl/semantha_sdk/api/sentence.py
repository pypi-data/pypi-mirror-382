from semantha_sdk.model.sentence import Sentence
from semantha_sdk.model.sentence import SentenceSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class SentenceEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/referencedocuments/{documentid}/sentences/{id}"
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
    ) -> Sentence:
        """
        Get one single sentence of specific document.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(SentenceSchema)

    
    
    
    