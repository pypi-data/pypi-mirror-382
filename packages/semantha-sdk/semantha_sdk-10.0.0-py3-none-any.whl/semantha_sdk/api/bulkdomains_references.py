from semantha_sdk.model.document import Document
from semantha_sdk.model.document import DocumentSchema
from semantha_sdk.model.mode_enum import ModeEnum
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class BulkdomainsReferencesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/domains/{domainname}/references"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/references"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        body: List[Document] = None,
        referencedocumentids: str = None,
        tags: str = None,
        documentclassids: str = None,
        similaritythreshold: float = None,
        synonymousthreshold: float = None,
        marknomatch: bool = None,
        withreferencetext: bool = None,
        withreferenceimage: bool = None,
        withareas: bool = None,
        mode: ModeEnum = None,
        detectlanguage: bool = None,
        maxreferences: int = None,
        considertexttype: bool = None,
        resizeparagraphs: bool = None,
    ) -> List[Document]:
        """
        Determine references with several input documents
            Matches several input documents ('file' parameter, as an alternative 'text' can be used) to a set of 'referencedocument' if set or internal library. If you match against internal library the 'tags' parameter can be used to filter the library.
        Args:
        body (List[Document]): 
        """
        q_params = {}
        if referencedocumentids is not None:
            q_params["referencedocumentids"] = referencedocumentids
        if tags is not None:
            q_params["tags"] = tags
        if documentclassids is not None:
            q_params["documentclassids"] = documentclassids
        if similaritythreshold is not None:
            q_params["similaritythreshold"] = similaritythreshold
        if synonymousthreshold is not None:
            q_params["synonymousthreshold"] = synonymousthreshold
        if marknomatch is not None:
            q_params["marknomatch"] = marknomatch
        if withreferencetext is not None:
            q_params["withreferencetext"] = withreferencetext
        if withreferenceimage is not None:
            q_params["withreferenceimage"] = withreferenceimage
        if withareas is not None:
            q_params["withareas"] = withareas
        if mode is not None:
            q_params["mode"] = mode
        if detectlanguage is not None:
            q_params["detectlanguage"] = detectlanguage
        if maxreferences is not None:
            q_params["maxreferences"] = maxreferences
        if considertexttype is not None:
            q_params["considertexttype"] = considertexttype
        if resizeparagraphs is not None:
            q_params["resizeparagraphs"] = resizeparagraphs
        response = self._session.post(
            url=self._endpoint,
            json=DocumentSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentSchema)

    
    
    