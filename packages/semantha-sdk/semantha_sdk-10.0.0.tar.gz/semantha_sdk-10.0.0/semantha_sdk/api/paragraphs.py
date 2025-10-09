from semantha_sdk.api.paragraph import ParagraphEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ParagraphsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/referencedocuments/{documentid}/paragraphs"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/paragraphs"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ParagraphEndpoint:
        return ParagraphEndpoint(self._session, self._endpoint, id)

    
    
    
    
    