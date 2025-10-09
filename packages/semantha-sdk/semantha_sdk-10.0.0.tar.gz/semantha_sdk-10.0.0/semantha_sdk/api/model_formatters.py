from semantha_sdk.model.formatter import Formatter
from semantha_sdk.model.formatter import FormatterSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelFormattersEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/formatters"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/formatters"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
    ) -> List[Formatter]:
        """
        Get all formatters
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(FormatterSchema)

    
    
    
    