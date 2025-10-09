from semantha_sdk.model.document_class_bulk import DocumentClassBulk
from semantha_sdk.model.document_class_bulk import DocumentClassBulkSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class BulkdomainsDocumentclassesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/domains/{domainname}/documentclasses"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/documentclasses"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def get(
        self,
    ) -> List[DocumentClassBulk]:
        """
        Get all document classes
            This is the quiet version of  'get /api/domains/{domainname}/documentclasses'
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentClassBulkSchema)

    def post(
        self,
        body: List[DocumentClassBulk] = None,
    ) -> None:
        """
        Create one or more document classes
            This is the quiet version of  'post /api/domains/{domainname}/documentclasses'
        Args:
        body (List[DocumentClassBulk]): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=DocumentClassBulkSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    
    