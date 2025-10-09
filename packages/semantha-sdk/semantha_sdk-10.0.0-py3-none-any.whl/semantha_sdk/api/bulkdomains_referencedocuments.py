from io import IOBase
from semantha_sdk.model.document import Document
from semantha_sdk.model.document import DocumentSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class BulkdomainsReferencedocumentsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/bulk/domains/{domainname}/referencedocuments"
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

    def get(
        self,
        withsentences: bool = None,
    ) -> List[Document]:
        """
        Get all reference documents
            This is the quiet version of  'get /api/domains/{domainname}/referencedocuments'
        Args:
        withsentences bool: Gives back the sentences of a paragraph.
        """
        q_params = {}
        if withsentences is not None:
            q_params["withsentences"] = withsentences
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DocumentSchema)

    def post(
        self,
        name: str = None,
        tags: str = None,
        metadata: str = None,
        file: IOBase = None,
        text: str = None,
        documenttype: str = None,
        color: str = None,
        comment: str = None,
        documentclassid: str = None,
        addparagraphsasdocuments: bool = None,
        detectlanguage: bool = None,
        linkclasses: bool = None,
    ) -> None:
        """
        Upload reference document
            This is the quiet version of  'post /api/domains/{domainname}/referencedocuments'
        Args:
        name (str): The document name in your library (in contrast to the file name being used during upload).
    tags (str): List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    metadata (str): Filter by metadata
    file (IOBase): Input document (left document).
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    color (str): Use this parameter to specify the color for your reference document. Possible values are RED, MAGENTA, AQUA, ORANGE, GREY, or LAVENDER.
    comment (str): Use this parameter to add a comment to your reference document.
    documentclassid (str): List of documentclass ID for the target. The limit here is 1 ID.
    addparagraphsasdocuments (bool): Use this parameter to create individual reference documents in the library for each paragraph in your document. The parameter is of type boolean and is set to false by default.
        """
        q_params = {}
        if detectlanguage is not None:
            q_params["detectlanguage"] = detectlanguage
        if linkclasses is not None:
            q_params["linkclasses"] = linkclasses
        response = self._session.post(
            url=self._endpoint,
            body={
                "name": name,
                "tags": tags,
                "metadata": metadata,
                "file": file,
                "text": text,
                "documenttype": documenttype,
                "color": color,
                "comment": comment,
                "documentclassid": documentclassid,
                "addparagraphsasdocuments": addparagraphsasdocuments,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()
    def post_json(
        self,
        body: List[Document] = None,
        detectlanguage: bool = None,
        linkclasses: bool = None,
    ) -> None:
        """
        Upload reference document
            This is the quiet version of  'post /api/domains/{domainname}/referencedocuments'
        Args:
        body (List[Document]): 
        """
        q_params = {}
        if detectlanguage is not None:
            q_params["detectlanguage"] = detectlanguage
        if linkclasses is not None:
            q_params["linkclasses"] = linkclasses
        response = self._session.post(
            url=self._endpoint,
            json=DocumentSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    def delete(
        self,
        body: List[str],
    ) -> None:
        """
        
        """
        self._session.delete(
            url=self._endpoint,
            json=body
        ).execute()

    