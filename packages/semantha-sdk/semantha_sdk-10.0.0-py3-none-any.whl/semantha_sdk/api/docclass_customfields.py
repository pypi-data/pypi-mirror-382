from semantha_sdk.model.custom_field import CustomField
from semantha_sdk.model.custom_field import CustomFieldSchema
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class DocclassCustomfieldsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documentclasses/{id}/customfields"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/customfields"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    
    
    def delete(
        self,
    ) -> None:
        """
        
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: List[CustomField]
    ) -> None:
        """
        
        """
        return self._session.put(
            url=self._endpoint,
            json=CustomFieldSchema().dump(body, many=True)
        ).execute().as_none()
