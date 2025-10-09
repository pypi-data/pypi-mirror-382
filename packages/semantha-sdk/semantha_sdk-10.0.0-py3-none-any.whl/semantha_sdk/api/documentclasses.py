from semantha_sdk.api.documentclass import DocumentclassEndpoint
from semantha_sdk.model.document_class import DocumentClass
from semantha_sdk.model.document_class import DocumentClassSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class DocumentclassesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documentclasses"
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

    def __call__(
            self,
            id: str,
    ) -> DocumentclassEndpoint:
        return DocumentclassEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[DocumentClass]:
        """
        Get all document classes
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentClassSchema)

    def post(
        self,
        body: DocumentClass = None,
    ) -> DocumentClass:
        """
        Create one or more document classes
        Args:
        body (DocumentClass): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=DocumentClassSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentClassSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all document classes
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    