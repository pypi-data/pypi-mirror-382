from semantha_sdk.model.instance import Instance
from semantha_sdk.model.instance import InstanceSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelontclassInstancesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/classes/{classid}/instances"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/instances"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
    ) -> List[Instance]:
        """
        Get all instances of a specific class
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(InstanceSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        Delete all instances of a specific class
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    