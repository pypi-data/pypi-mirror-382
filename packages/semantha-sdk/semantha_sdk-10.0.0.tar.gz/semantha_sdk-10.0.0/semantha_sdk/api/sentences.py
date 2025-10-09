from semantha_sdk.api.sentence import SentenceEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class SentencesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/referencedocuments/{documentid}/sentences"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/sentences"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> SentenceEndpoint:
        return SentenceEndpoint(self._session, self._endpoint, id)

    
    
    
    
    