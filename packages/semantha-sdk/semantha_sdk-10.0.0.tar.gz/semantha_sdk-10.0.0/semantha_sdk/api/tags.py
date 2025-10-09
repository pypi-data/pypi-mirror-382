from semantha_sdk.api.tag import TagEndpoint
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class TagsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/tags"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/tags"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            tagname: str,
    ) -> TagEndpoint:
        return TagEndpoint(self._session, self._endpoint, tagname)

    def get(
        self,
    ) -> List[str]:
        """
        Get tags
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().as_list()

    
    
    
    