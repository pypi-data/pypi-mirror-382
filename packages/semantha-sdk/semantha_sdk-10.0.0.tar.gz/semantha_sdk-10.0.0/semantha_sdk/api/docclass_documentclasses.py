from semantha_sdk.model.document_class import DocumentClass
from semantha_sdk.model.document_class import DocumentClassSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class DocclassDocumentclassesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documentclasses/{id}/documentclasses"
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
    ) -> List[DocumentClass]:
        """
        Get all subclasses for a document class identified by id
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentClassSchema)

    def post(
        self,
        body: DocumentClass = None,
    ) -> DocumentClass:
        """
        Create one or more subclasses for a document class identified by name
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

    def patch(
        self,
        body: List[str]
    ) -> List[DocumentClass]:
        """
        Add existing classes as subclasses to a document class identified by id
        """
        return self._session.patch(
            url=self._endpoint,
            json=body
        ).execute().to(DocumentClassSchema)

    def delete(
        self,
        body: List[str],
    ) -> None:
        """
        Delete a subclass from a document class identified by id
        """
        self._session.delete(
            url=self._endpoint,
            json=body
        ).execute()

    