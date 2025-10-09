from semantha_sdk.api.docclass_customfields import DocclassCustomfieldsEndpoint
from semantha_sdk.api.docclass_documentclasses import DocclassDocumentclassesEndpoint
from semantha_sdk.api.docclass_referencedocuments import DocclassReferencedocumentsEndpoint
from semantha_sdk.model.document_class import DocumentClass
from semantha_sdk.model.document_class import DocumentClassSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class DocumentclassEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documentclasses/{id}"
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
        self.__customfields = DocclassCustomfieldsEndpoint(session, self._endpoint)
        self.__documentclasses = DocclassDocumentclassesEndpoint(session, self._endpoint)
        self.__referencedocuments = DocclassReferencedocumentsEndpoint(session, self._endpoint)

    @property
    def customfields(self) -> DocclassCustomfieldsEndpoint:
        return self.__customfields

    @property
    def documentclasses(self) -> DocclassDocumentclassesEndpoint:
        return self.__documentclasses

    @property
    def referencedocuments(self) -> DocclassReferencedocumentsEndpoint:
        return self.__referencedocuments

    def get(
        self,
    ) -> DocumentClass:
        """
        Get a class identified by id and all its subclasses
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentClassSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        Delete a document class identified by id
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: DocumentClass
    ) -> DocumentClass:
        """
        Rename a document class identified by its id
        """
        return self._session.put(
            url=self._endpoint,
            json=DocumentClassSchema().dump(body)
        ).execute().to(DocumentClassSchema)
