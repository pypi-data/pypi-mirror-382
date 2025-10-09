from semantha_sdk.api.modelont_attribute import ModelontAttributeEndpoint
from semantha_sdk.model.attribute import Attribute
from semantha_sdk.model.attribute import AttributeSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelontAttributesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/classes/{classid}/attributes"
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

    def __call__(
            self,
            id: str,
    ) -> ModelontAttributeEndpoint:
        return ModelontAttributeEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[Attribute]:
        """
        
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(AttributeSchema)

    def post(
        self,
        body: Attribute = None,
    ) -> Attribute:
        """
        
        Args:
        body (Attribute): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=AttributeSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(AttributeSchema)

    
    def delete(
        self,
    ) -> None:
        """
        
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    