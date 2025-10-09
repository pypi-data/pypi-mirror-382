from semantha_sdk.api.image import ImageEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ImagesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/referencedocuments/{documentid}/images"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/images"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ImageEndpoint:
        return ImageEndpoint(self._session, self._endpoint, id)

    
    
    
    
    