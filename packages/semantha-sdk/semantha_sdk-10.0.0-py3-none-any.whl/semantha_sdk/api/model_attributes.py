from semantha_sdk.model.attribute_overview import AttributeOverview
from semantha_sdk.model.attribute_overview import AttributeOverviewSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelAttributesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/attributes"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/attributes"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
    ) -> List[AttributeOverview]:
        """
        Get all attributes
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(AttributeOverviewSchema)

    
    
    
    