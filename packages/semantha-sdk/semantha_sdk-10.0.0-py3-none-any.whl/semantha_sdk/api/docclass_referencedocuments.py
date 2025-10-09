from semantha_sdk.api.docclass_tags import DocclassTagsEndpoint
from semantha_sdk.model.document_information import DocumentInformation
from semantha_sdk.model.document_information import DocumentInformationSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class DocclassReferencedocumentsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documentclasses/{id}/referencedocuments"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/referencedocuments"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self.__tags = DocclassTagsEndpoint(session, self._endpoint)

    @property
    def tags(self) -> DocclassTagsEndpoint:
        return self.__tags

    def get(
        self,
    ) -> List[DocumentInformation]:
        """
        Get all library documents belonging to a document class identified by its id
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentInformationSchema)

    
    def patch(
        self,
        body: List[str]
    ) -> None:
        """
        Add a library document to a document class identified by its id
        """
        return self._session.patch(
            url=self._endpoint,
            json=body
        ).execute().as_none()

    def delete(
        self,
        body: List[str],
    ) -> None:
        """
        Delete library documents from a document class identified by its id
        """
        self._session.delete(
            url=self._endpoint,
            json=body
        ).execute()

    