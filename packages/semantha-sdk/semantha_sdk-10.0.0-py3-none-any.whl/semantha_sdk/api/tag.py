from semantha_sdk.api.tag_referencedocuments import TagReferencedocumentsEndpoint
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class TagEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/tags/{tagname}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._tagname}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        tagname: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._tagname = tagname
        self.__referencedocuments = TagReferencedocumentsEndpoint(session, self._endpoint)

    @property
    def referencedocuments(self) -> TagReferencedocumentsEndpoint:
        return self.__referencedocuments

    
    
    
    
    