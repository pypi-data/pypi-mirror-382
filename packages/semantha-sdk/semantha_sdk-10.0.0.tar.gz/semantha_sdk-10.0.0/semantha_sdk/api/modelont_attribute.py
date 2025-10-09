from semantha_sdk.model.attribute import Attribute
from semantha_sdk.model.attribute import AttributeSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelontAttributeEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/model/domains/{domainname}/classes/{classid}/attributes/{id}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._id}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        id: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._id = id

    def get(
        self,
    ) -> Attribute:
        """
        
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(AttributeSchema)

    
    
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
        body: Attribute
    ) -> Attribute:
        """
        
        """
        return self._session.put(
            url=self._endpoint,
            json=AttributeSchema().dump(body)
        ).execute().to(AttributeSchema)
