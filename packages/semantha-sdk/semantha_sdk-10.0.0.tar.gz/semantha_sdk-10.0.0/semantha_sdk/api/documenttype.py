from semantha_sdk.api.clone import CloneEndpoint
from semantha_sdk.model.document_type import DocumentType
from semantha_sdk.model.document_type import DocumentTypeSchema
from semantha_sdk.model.document_type_change import DocumentTypeChange
from semantha_sdk.model.document_type_change import DocumentTypeChangeSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class DocumenttypeEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documenttypes/{id}"
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
        self.__clone = CloneEndpoint(session, self._endpoint)

    @property
    def clone(self) -> CloneEndpoint:
        return self.__clone

    def get(
        self,
    ) -> DocumentType:
        """
        Read one document type.
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentTypeSchema)

    
    def patch(
        self,
        body: DocumentTypeChange
    ) -> DocumentType:
        """
        Change one document type. Needs roles: 'Advanced User', 'Domain Admin' or 'Expert User'
        """
        return self._session.patch(
            url=self._endpoint,
            json=DocumentTypeChangeSchema().dump(body)
        ).execute().to(DocumentTypeSchema)

    def delete(
        self,
    ) -> None:
        """
        Delete one document type. Needs roles: 'Advanced User', 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    