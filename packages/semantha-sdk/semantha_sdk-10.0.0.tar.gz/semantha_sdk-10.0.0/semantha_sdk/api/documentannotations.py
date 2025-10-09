from io import IOBase
from semantha_sdk.model.document import Document
from semantha_sdk.model.document import DocumentSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class DocumentannotationsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documentannotations"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/documentannotations"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post_as_docx(
        self,
        file: IOBase = None,
        document: Document = None,
        similaritythreshold: float = None,
        synonymousthreshold: float = None,
        marknomatch: bool = None,
        withreferencetext: bool = None,
    ) -> IOBase:
        """
        Download the original input document (pdf or docx) with the referenced document/library matches as annotated comments
        Args:
        file (IOBase): Input document (left document).
    document (Document): 
    similaritythreshold (float): Threshold for the similarity score. semantha will not deliver results with a sentence score lower than the threshold.
            In general, the higher the threshold, the more precise the results.
    synonymousthreshold (float): Threshold for good matches.
    marknomatch (bool): Marks the paragraphs that have not matched
    withreferencetext (bool): Provide the reference text in the result JSON. If set to false, you have to query the library to resolve the references yourself.
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "document": document,
                "similaritythreshold": similaritythreshold,
                "synonymousthreshold": synonymousthreshold,
                "marknomatch": marknomatch,
                "withreferencetext": withreferencetext,
            },
            headers=RestClient.to_header(MediaType.DOCX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()
    def post_as_pdf(
        self,
        file: IOBase = None,
        document: Document = None,
        similaritythreshold: float = None,
        synonymousthreshold: float = None,
        marknomatch: bool = None,
        withreferencetext: bool = None,
    ) -> IOBase:
        """
        Download the original input document (pdf or docx) with the referenced document/library matches as annotated comments
        Args:
        file (IOBase): Input document (left document).
    document (Document): 
    similaritythreshold (float): Threshold for the similarity score. semantha will not deliver results with a sentence score lower than the threshold.
            In general, the higher the threshold, the more precise the results.
    synonymousthreshold (float): Threshold for good matches.
    marknomatch (bool): Marks the paragraphs that have not matched
    withreferencetext (bool): Provide the reference text in the result JSON. If set to false, you have to query the library to resolve the references yourself.
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "document": document,
                "similaritythreshold": similaritythreshold,
                "synonymousthreshold": synonymousthreshold,
                "marknomatch": marknomatch,
                "withreferencetext": withreferencetext,
            },
            headers=RestClient.to_header(MediaType.PDF),
            q_params=q_params
        ).execute()
        return response.as_bytesio()

    
    
    