from semantha_sdk.model.document_type import DocumentType
from semantha_sdk.model.document_type import DocumentTypeSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class BulkdomainsDocumenttypesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/domains/{domainname}/documenttypes"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/documenttypes"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
    ) -> List[DocumentType]:
        """
        
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentTypeSchema)

    def post(
        self,
        body: List[DocumentType] = None,
    ) -> None:
        """
        
        Args:
        body (List[DocumentType]): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=DocumentTypeSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    
    