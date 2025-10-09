from semantha_sdk.api.images import ImagesEndpoint
from semantha_sdk.api.paragraphs import ParagraphsEndpoint
from semantha_sdk.api.sentences import SentencesEndpoint
from semantha_sdk.model.document import Document
from semantha_sdk.model.document import DocumentSchema
from semantha_sdk.model.document_information import DocumentInformation
from semantha_sdk.model.document_information import DocumentInformationSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ReferencedocumentEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/referencedocuments/{documentid}"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._documentid}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        documentid: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._documentid = documentid
        self.__images = ImagesEndpoint(session, self._endpoint)
        self.__paragraphs = ParagraphsEndpoint(session, self._endpoint)
        self.__sentences = SentencesEndpoint(session, self._endpoint)

    @property
    def images(self) -> ImagesEndpoint:
        return self.__images

    @property
    def paragraphs(self) -> ParagraphsEndpoint:
        return self.__paragraphs

    @property
    def sentences(self) -> SentencesEndpoint:
        return self.__sentences

    def get(
        self,
        querybyname: bool = None,
    ) -> Document:
        """
        Returns one reference document by ID.
        Args:
        querybyname bool: If true, documentid is treated as name and we search for a document with a given name.
        """
        q_params = {}
        if querybyname is not None:
            q_params["querybyname"] = querybyname
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentSchema)

    
    def patch(
        self,
        body: DocumentInformation
    ) -> DocumentInformation:
        """
        Change one reference document. Needs roles: 'Domain Admin' or 'Expert User'
        """
        return self._session.patch(
            url=self._endpoint,
            json=DocumentInformationSchema().dump(body)
        ).execute().to(DocumentInformationSchema)

    def delete(
        self,
    ) -> None:
        """
        Delete one reference document. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    