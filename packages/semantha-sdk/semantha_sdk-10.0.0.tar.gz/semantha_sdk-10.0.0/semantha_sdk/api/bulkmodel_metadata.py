from semantha_sdk.model.model_metadata import ModelMetadata
from semantha_sdk.model.model_metadata import ModelMetadataSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class BulkmodelMetadataEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/model/domains/{domainname}/metadata"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/metadata"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
    ) -> List[ModelMetadata]:
        """
        Get all metadata
            This is the quiet version of  'get /api/domains/{domainname}/metadata'
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(ModelMetadataSchema)

    def post(
        self,
        body: List[ModelMetadata] = None,
    ) -> None:
        """
        Create one or more metadata
            This is the quiet version of  'post /api/domains/{domainname}/metadata'
        Args:
        body (List[ModelMetadata]): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=ModelMetadataSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    
    