from io import IOBase
from semantha_sdk.model.document import Document
from semantha_sdk.model.document import DocumentSchema
from semantha_sdk.model.document_meta_data import DocumentMetaData
from semantha_sdk.model.document_meta_data import DocumentMetaDataSchema
from semantha_sdk.model.mode_enum import ModeEnum
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ReferencesEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/references"
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
        file: IOBase = None,
        referencedocument: IOBase = None,
        referencedocumentids: List[str] = None,
        tags: str = None,
        documentclassids: List[str] = None,
        similaritythreshold: float = None,
        synonymousthreshold: float = None,
        marknomatch: bool = None,
        withreferencetext: bool = None,
        mode: ModeEnum = None,
        documenttype: str = None,
        metadata: List[DocumentMetaData] = None,
        considertexttype: bool = None,
        resizeparagraphs: bool = None,
        text: str = None,
        withreferenceimage: bool = None,
        withareas: bool = None,
        detectlanguage: bool = None,
        maxreferences: int = None,
    ) -> Document:
        """
        Determine references with one input document
            Returns the input document (file) with its references. Depending on the 'Accept' header different output formats are supported. For 'application/json' we return the document with references. For xlsx we return an Excel sheet with each reference as rows. If input and output is docx or pdf we return the document with comments on paragraphs.
        Args:
        file (IOBase): Input document (left document).
    referencedocument (IOBase): Reference document(s) to be used instead of the documents in the domain's library.
    referencedocumentids (List[str]): To filter for document IDs. The limit here is 65000 IDs.
            The IDs are passed as a JSON array.
    tags (str): List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentclassids (List[str]): List of documentclass IDs for the target. The limit here is 1000 IDs.
            The IDs are passed as a JSON array.
            This does not apply on the GET referencedocuments call. Here the ids are separated with a comma.
    similaritythreshold (float): Threshold for the similarity score. semantha will not deliver results with a sentence score lower than the threshold.
            In general, the higher the threshold, the more precise the results.
    synonymousthreshold (float): Threshold for good matches.
    marknomatch (bool): Marks the paragraphs that have not matched
    withreferencetext (bool): Provide the reference text in the result JSON. If set to false, you have to query the library to resolve the references yourself.
    mode (ModeEnum): When using the references endpoint: Use mode to determine the type of search semantha should perform. 
            fingerprint: semantic search based on sentences; 
            keyword: keyword: search based on sentences; 
            document: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. Higher scores indicate higher similarity. Please note that the similarity score has no upper limit and is not normalized; 
            document_fingerprint: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. The results are then reranked based on a semantic search. This reranking results in normalized scores and as such represents an enhancement of the mode document; 
            fingerprint_keyword (formerly auto): semantic search, if no results are found a keyword search is performed
            Creating document model: It also defines what structure should be considered for what operator (similarity or extraction).
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    metadata (List[DocumentMetaData]): Filter by metadata
    considertexttype (bool): Use this parameter to ensure that only paragraphs of the same type are compared with each other. The parameter is of type boolean and is set to false by default.
    resizeparagraphs (bool): Automatically resizes paragraphs based on their semantic meaning.
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    withreferenceimage (bool): 
    withareas (bool): Gives back the coordinates of sentences.
        """
        q_params = {}
        if detectlanguage is not None:
            q_params["detectlanguage"] = detectlanguage
        if maxreferences is not None:
            q_params["maxreferences"] = maxreferences
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "referencedocument": referencedocument,
                "referencedocumentids": referencedocumentids,
                "tags": tags,
                "documentclassids": documentclassids,
                "similaritythreshold": similaritythreshold,
                "synonymousthreshold": synonymousthreshold,
                "marknomatch": marknomatch,
                "withreferencetext": withreferencetext,
                "mode": mode,
                "documenttype": documenttype,
                "metadata": metadata,
                "considertexttype": considertexttype,
                "resizeparagraphs": resizeparagraphs,
                "text": text,
                "withreferenceimage": withreferenceimage,
                "withareas": withareas,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentSchema)
    def post_as_xlsx(
        self,
        file: IOBase = None,
        referencedocument: IOBase = None,
        referencedocumentids: List[str] = None,
        tags: str = None,
        documentclassids: List[str] = None,
        similaritythreshold: float = None,
        synonymousthreshold: float = None,
        marknomatch: bool = None,
        withreferencetext: bool = None,
        mode: ModeEnum = None,
        documenttype: str = None,
        metadata: List[DocumentMetaData] = None,
        considertexttype: bool = None,
        resizeparagraphs: bool = None,
        text: str = None,
        withreferenceimage: bool = None,
        withareas: bool = None,
        detectlanguage: bool = None,
        maxreferences: int = None,
    ) -> IOBase:
        """
        Determine references with one input document
            Returns the input document (file) with its references. Depending on the 'Accept' header different output formats are supported. For 'application/json' we return the document with references. For xlsx we return an Excel sheet with each reference as rows. If input and output is docx or pdf we return the document with comments on paragraphs.
        Args:
        file (IOBase): Input document (left document).
    referencedocument (IOBase): Reference document(s) to be used instead of the documents in the domain's library.
    referencedocumentids (List[str]): To filter for document IDs. The limit here is 65000 IDs.
            The IDs are passed as a JSON array.
    tags (str): List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentclassids (List[str]): List of documentclass IDs for the target. The limit here is 1000 IDs.
            The IDs are passed as a JSON array.
            This does not apply on the GET referencedocuments call. Here the ids are separated with a comma.
    similaritythreshold (float): Threshold for the similarity score. semantha will not deliver results with a sentence score lower than the threshold.
            In general, the higher the threshold, the more precise the results.
    synonymousthreshold (float): Threshold for good matches.
    marknomatch (bool): Marks the paragraphs that have not matched
    withreferencetext (bool): Provide the reference text in the result JSON. If set to false, you have to query the library to resolve the references yourself.
    mode (ModeEnum): When using the references endpoint: Use mode to determine the type of search semantha should perform. 
            fingerprint: semantic search based on sentences; 
            keyword: keyword: search based on sentences; 
            document: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. Higher scores indicate higher similarity. Please note that the similarity score has no upper limit and is not normalized; 
            document_fingerprint: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. The results are then reranked based on a semantic search. This reranking results in normalized scores and as such represents an enhancement of the mode document; 
            fingerprint_keyword (formerly auto): semantic search, if no results are found a keyword search is performed
            Creating document model: It also defines what structure should be considered for what operator (similarity or extraction).
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    metadata (List[DocumentMetaData]): Filter by metadata
    considertexttype (bool): Use this parameter to ensure that only paragraphs of the same type are compared with each other. The parameter is of type boolean and is set to false by default.
    resizeparagraphs (bool): Automatically resizes paragraphs based on their semantic meaning.
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    withreferenceimage (bool): 
    withareas (bool): Gives back the coordinates of sentences.
        """
        q_params = {}
        if detectlanguage is not None:
            q_params["detectlanguage"] = detectlanguage
        if maxreferences is not None:
            q_params["maxreferences"] = maxreferences
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "referencedocument": referencedocument,
                "referencedocumentids": referencedocumentids,
                "tags": tags,
                "documentclassids": documentclassids,
                "similaritythreshold": similaritythreshold,
                "synonymousthreshold": synonymousthreshold,
                "marknomatch": marknomatch,
                "withreferencetext": withreferencetext,
                "mode": mode,
                "documenttype": documenttype,
                "metadata": metadata,
                "considertexttype": considertexttype,
                "resizeparagraphs": resizeparagraphs,
                "text": text,
                "withreferenceimage": withreferenceimage,
                "withareas": withareas,
            },
            headers=RestClient.to_header(MediaType.XLSX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()
    def post_as_docx(
        self,
        file: IOBase = None,
        referencedocument: IOBase = None,
        referencedocumentids: List[str] = None,
        tags: str = None,
        documentclassids: List[str] = None,
        similaritythreshold: float = None,
        synonymousthreshold: float = None,
        marknomatch: bool = None,
        withreferencetext: bool = None,
        mode: ModeEnum = None,
        documenttype: str = None,
        metadata: List[DocumentMetaData] = None,
        considertexttype: bool = None,
        resizeparagraphs: bool = None,
        text: str = None,
        withreferenceimage: bool = None,
        withareas: bool = None,
        detectlanguage: bool = None,
        maxreferences: int = None,
    ) -> IOBase:
        """
        Determine references with one input document
            Returns the input document (file) with its references. Depending on the 'Accept' header different output formats are supported. For 'application/json' we return the document with references. For xlsx we return an Excel sheet with each reference as rows. If input and output is docx or pdf we return the document with comments on paragraphs.
        Args:
        file (IOBase): Input document (left document).
    referencedocument (IOBase): Reference document(s) to be used instead of the documents in the domain's library.
    referencedocumentids (List[str]): To filter for document IDs. The limit here is 65000 IDs.
            The IDs are passed as a JSON array.
    tags (str): List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentclassids (List[str]): List of documentclass IDs for the target. The limit here is 1000 IDs.
            The IDs are passed as a JSON array.
            This does not apply on the GET referencedocuments call. Here the ids are separated with a comma.
    similaritythreshold (float): Threshold for the similarity score. semantha will not deliver results with a sentence score lower than the threshold.
            In general, the higher the threshold, the more precise the results.
    synonymousthreshold (float): Threshold for good matches.
    marknomatch (bool): Marks the paragraphs that have not matched
    withreferencetext (bool): Provide the reference text in the result JSON. If set to false, you have to query the library to resolve the references yourself.
    mode (ModeEnum): When using the references endpoint: Use mode to determine the type of search semantha should perform. 
            fingerprint: semantic search based on sentences; 
            keyword: keyword: search based on sentences; 
            document: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. Higher scores indicate higher similarity. Please note that the similarity score has no upper limit and is not normalized; 
            document_fingerprint: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. The results are then reranked based on a semantic search. This reranking results in normalized scores and as such represents an enhancement of the mode document; 
            fingerprint_keyword (formerly auto): semantic search, if no results are found a keyword search is performed
            Creating document model: It also defines what structure should be considered for what operator (similarity or extraction).
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    metadata (List[DocumentMetaData]): Filter by metadata
    considertexttype (bool): Use this parameter to ensure that only paragraphs of the same type are compared with each other. The parameter is of type boolean and is set to false by default.
    resizeparagraphs (bool): Automatically resizes paragraphs based on their semantic meaning.
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    withreferenceimage (bool): 
    withareas (bool): Gives back the coordinates of sentences.
        """
        q_params = {}
        if detectlanguage is not None:
            q_params["detectlanguage"] = detectlanguage
        if maxreferences is not None:
            q_params["maxreferences"] = maxreferences
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "referencedocument": referencedocument,
                "referencedocumentids": referencedocumentids,
                "tags": tags,
                "documentclassids": documentclassids,
                "similaritythreshold": similaritythreshold,
                "synonymousthreshold": synonymousthreshold,
                "marknomatch": marknomatch,
                "withreferencetext": withreferencetext,
                "mode": mode,
                "documenttype": documenttype,
                "metadata": metadata,
                "considertexttype": considertexttype,
                "resizeparagraphs": resizeparagraphs,
                "text": text,
                "withreferenceimage": withreferenceimage,
                "withareas": withareas,
            },
            headers=RestClient.to_header(MediaType.DOCX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()
    def post_as_pdf(
        self,
        file: IOBase = None,
        referencedocument: IOBase = None,
        referencedocumentids: List[str] = None,
        tags: str = None,
        documentclassids: List[str] = None,
        similaritythreshold: float = None,
        synonymousthreshold: float = None,
        marknomatch: bool = None,
        withreferencetext: bool = None,
        mode: ModeEnum = None,
        documenttype: str = None,
        metadata: List[DocumentMetaData] = None,
        considertexttype: bool = None,
        resizeparagraphs: bool = None,
        text: str = None,
        withreferenceimage: bool = None,
        withareas: bool = None,
        detectlanguage: bool = None,
        maxreferences: int = None,
    ) -> IOBase:
        """
        Determine references with one input document
            Returns the input document (file) with its references. Depending on the 'Accept' header different output formats are supported. For 'application/json' we return the document with references. For xlsx we return an Excel sheet with each reference as rows. If input and output is docx or pdf we return the document with comments on paragraphs.
        Args:
        file (IOBase): Input document (left document).
    referencedocument (IOBase): Reference document(s) to be used instead of the documents in the domain's library.
    referencedocumentids (List[str]): To filter for document IDs. The limit here is 65000 IDs.
            The IDs are passed as a JSON array.
    tags (str): List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentclassids (List[str]): List of documentclass IDs for the target. The limit here is 1000 IDs.
            The IDs are passed as a JSON array.
            This does not apply on the GET referencedocuments call. Here the ids are separated with a comma.
    similaritythreshold (float): Threshold for the similarity score. semantha will not deliver results with a sentence score lower than the threshold.
            In general, the higher the threshold, the more precise the results.
    synonymousthreshold (float): Threshold for good matches.
    marknomatch (bool): Marks the paragraphs that have not matched
    withreferencetext (bool): Provide the reference text in the result JSON. If set to false, you have to query the library to resolve the references yourself.
    mode (ModeEnum): When using the references endpoint: Use mode to determine the type of search semantha should perform. 
            fingerprint: semantic search based on sentences; 
            keyword: keyword: search based on sentences; 
            document: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. Higher scores indicate higher similarity. Please note that the similarity score has no upper limit and is not normalized; 
            document_fingerprint: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. The results are then reranked based on a semantic search. This reranking results in normalized scores and as such represents an enhancement of the mode document; 
            fingerprint_keyword (formerly auto): semantic search, if no results are found a keyword search is performed
            Creating document model: It also defines what structure should be considered for what operator (similarity or extraction).
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    metadata (List[DocumentMetaData]): Filter by metadata
    considertexttype (bool): Use this parameter to ensure that only paragraphs of the same type are compared with each other. The parameter is of type boolean and is set to false by default.
    resizeparagraphs (bool): Automatically resizes paragraphs based on their semantic meaning.
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    withreferenceimage (bool): 
    withareas (bool): Gives back the coordinates of sentences.
        """
        q_params = {}
        if detectlanguage is not None:
            q_params["detectlanguage"] = detectlanguage
        if maxreferences is not None:
            q_params["maxreferences"] = maxreferences
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "referencedocument": referencedocument,
                "referencedocumentids": referencedocumentids,
                "tags": tags,
                "documentclassids": documentclassids,
                "similaritythreshold": similaritythreshold,
                "synonymousthreshold": synonymousthreshold,
                "marknomatch": marknomatch,
                "withreferencetext": withreferencetext,
                "mode": mode,
                "documenttype": documenttype,
                "metadata": metadata,
                "considertexttype": considertexttype,
                "resizeparagraphs": resizeparagraphs,
                "text": text,
                "withreferenceimage": withreferenceimage,
                "withareas": withareas,
            },
            headers=RestClient.to_header(MediaType.PDF),
            q_params=q_params
        ).execute()
        return response.as_bytesio()

    
    
    