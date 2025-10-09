from io import IOBase
from semantha_sdk.api.clusters import ClustersEndpoint
from semantha_sdk.api.namedentities import NamedentitiesEndpoint
from semantha_sdk.api.referencedocument import ReferencedocumentEndpoint
from semantha_sdk.api.statistic import StatisticEndpoint
from semantha_sdk.model.document import Document
from semantha_sdk.model.document import DocumentSchema
from semantha_sdk.model.document_information import DocumentInformation
from semantha_sdk.model.document_information import DocumentInformationSchema
from semantha_sdk.model.reference_documents_response_container import ReferenceDocumentsResponseContainer
from semantha_sdk.model.reference_documents_response_container import ReferenceDocumentsResponseContainerSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ReferencedocumentsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/referencedocuments"
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
        self.__clusters = ClustersEndpoint(session, self._endpoint)
        self.__namedentities = NamedentitiesEndpoint(session, self._endpoint)
        self.__statistic = StatisticEndpoint(session, self._endpoint)

    @property
    def clusters(self) -> ClustersEndpoint:
        return self.__clusters

    @property
    def namedentities(self) -> NamedentitiesEndpoint:
        return self.__namedentities

    @property
    def statistic(self) -> StatisticEndpoint:
        return self.__statistic

    def __call__(
            self,
            documentid: str,
    ) -> ReferencedocumentEndpoint:
        return ReferencedocumentEndpoint(self._session, self._endpoint, documentid)

    def get(
        self,
        tags: str = None,
        documentids: str = None,
        name: str = None,
        createdafter: int = None,
        createdbefore: int = None,
        updatedafter: int = None,
        updatedbefore: int = None,
        documentclassids: str = None,
        withoutdocumentclass: bool = None,
        mincharacters: int = None,
        metadata: str = None,
        comment: str = None,
        sourcedoc: bool = None,
        sourcedocumentid: str = None,
        offset: int = None,
        limit: int = None,
        sort: str = None,
        fields: str = None,
    ) -> ReferenceDocumentsResponseContainer:
        """
        Get all reference documents a.k.a. library items.
            Supports server side pagination and filtering for "application/json" media type only by using "offset" and "limit" query parameter.
            "Filter parameters:" name, createdbefore, createdafter, tags, documentclassids, metadata.
            Without "offset" and "limit" parameter, data can be filtered only by "tags" and "documentclassids".
        Args:
        tags str: List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentids str: List of document Ids for target. The limit here is 65000 IDs. The IDs can be passed as a comma separated string.
    name str: Filter documents for a given name
    createdafter int: Filter for documents which are created after a given UNIX timestamp. The createdafter filter only works when also using the parameters offset and limit.
    createdbefore int: Filter for documents which are created before a given UNIX timestamp. The createdbefore filter only works when also using the parameters offset and limit.
    updatedafter int: Filter for documents which are updated after a given UNIX timestamp. The updatedafter filter only works when also using the parameters offset and limit.
    updatedbefore int: Filter for documents which are updated before a given UNIX timestamp. The updatedbefore filter only works when also using the parameters offset and limit.
    documentclassids str: List of documentclass IDs for the target. The limit here is 1000 IDs. The IDs are passed as a comma separated list.
    withoutdocumentclass bool: Filters the returned reference documents to include only documents that are not linked to a documentclass. The parameter is of type boolean and is set to false by default.
    mincharacters int: Filters the returned reference documents to include only documents that have a minimum of characters
    metadata str: Filter documents for part of metadata, casing is ignored.
    comment str: Filter documents for part of comment, casing is ignored.
    sourcedoc bool: If true, then only source documents are returned.
    sourcedocumentid str: Filter documents a specific source document.
    offset int: Specify from which number on reference documents should be returned.
    limit int: Specify the number of reference documents to be returned.
    sort str: Define by which fields the returned reference documents are sorted. The following values can be sent as a comma-separated list: 'name', 'filename', 'metadata', 'created', 'updated', 'color', 'comment', 'derivedcolor', 'derivedcomment', 'documentclass'. Add a - before the field name to sort in descending order. Example: "documentclass,-created".
    fields str: Define which fields should be returned by the /referencedocuments endpoints. The following values can be sent as a comma-separated list: 'id', 'name', 'tags', 'derivedtags', 'metadata', 'filename', 'created', 'processed', 'lang', 'updated, color, derivedcolor, comment, derivedcomment, documentclass, contentpreview'. If empty or null all fields will be returned. Example: "id,name,contentpreview,tags"
        """
        q_params = {}
        if tags is not None:
            q_params["tags"] = tags
        if documentids is not None:
            q_params["documentids"] = documentids
        if name is not None:
            q_params["name"] = name
        if createdafter is not None:
            q_params["createdafter"] = createdafter
        if createdbefore is not None:
            q_params["createdbefore"] = createdbefore
        if updatedafter is not None:
            q_params["updatedafter"] = updatedafter
        if updatedbefore is not None:
            q_params["updatedbefore"] = updatedbefore
        if documentclassids is not None:
            q_params["documentclassids"] = documentclassids
        if withoutdocumentclass is not None:
            q_params["withoutdocumentclass"] = withoutdocumentclass
        if mincharacters is not None:
            q_params["mincharacters"] = mincharacters
        if metadata is not None:
            q_params["metadata"] = metadata
        if comment is not None:
            q_params["comment"] = comment
        if sourcedoc is not None:
            q_params["sourcedoc"] = sourcedoc
        if sourcedocumentid is not None:
            q_params["sourcedocumentid"] = sourcedocumentid
        if offset is not None:
            q_params["offset"] = offset
        if limit is not None:
            q_params["limit"] = limit
        if sort is not None:
            q_params["sort"] = sort
        if fields is not None:
            q_params["fields"] = fields
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(ReferenceDocumentsResponseContainerSchema)
    def get_as_xlsx(
        self,
        tags: str = None,
        documentids: str = None,
        name: str = None,
        createdafter: int = None,
        createdbefore: int = None,
        updatedafter: int = None,
        updatedbefore: int = None,
        documentclassids: str = None,
        withoutdocumentclass: bool = None,
        mincharacters: int = None,
        metadata: str = None,
        comment: str = None,
        sourcedoc: bool = None,
        sourcedocumentid: str = None,
        offset: int = None,
        limit: int = None,
        sort: str = None,
        fields: str = None,
    ) -> IOBase:
        """
        Get all reference documents a.k.a. library items.
            Supports server side pagination and filtering for "application/json" media type only by using "offset" and "limit" query parameter.
            "Filter parameters:" name, createdbefore, createdafter, tags, documentclassids, metadata.
            Without "offset" and "limit" parameter, data can be filtered only by "tags" and "documentclassids".
        Args:
        tags str: List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentids str: List of document Ids for target. The limit here is 65000 IDs. The IDs can be passed as a comma separated string.
    name str: Filter documents for a given name
    createdafter int: Filter for documents which are created after a given UNIX timestamp. The createdafter filter only works when also using the parameters offset and limit.
    createdbefore int: Filter for documents which are created before a given UNIX timestamp. The createdbefore filter only works when also using the parameters offset and limit.
    updatedafter int: Filter for documents which are updated after a given UNIX timestamp. The updatedafter filter only works when also using the parameters offset and limit.
    updatedbefore int: Filter for documents which are updated before a given UNIX timestamp. The updatedbefore filter only works when also using the parameters offset and limit.
    documentclassids str: List of documentclass IDs for the target. The limit here is 1000 IDs. The IDs are passed as a comma separated list.
    withoutdocumentclass bool: Filters the returned reference documents to include only documents that are not linked to a documentclass. The parameter is of type boolean and is set to false by default.
    mincharacters int: Filters the returned reference documents to include only documents that have a minimum of characters
    metadata str: Filter documents for part of metadata, casing is ignored.
    comment str: Filter documents for part of comment, casing is ignored.
    sourcedoc bool: If true, then only source documents are returned.
    sourcedocumentid str: Filter documents a specific source document.
    offset int: Specify from which number on reference documents should be returned.
    limit int: Specify the number of reference documents to be returned.
    sort str: Define by which fields the returned reference documents are sorted. The following values can be sent as a comma-separated list: 'name', 'filename', 'metadata', 'created', 'updated', 'color', 'comment', 'derivedcolor', 'derivedcomment', 'documentclass'. Add a - before the field name to sort in descending order. Example: "documentclass,-created".
    fields str: Define which fields should be returned by the /referencedocuments endpoints. The following values can be sent as a comma-separated list: 'id', 'name', 'tags', 'derivedtags', 'metadata', 'filename', 'created', 'processed', 'lang', 'updated, color, derivedcolor, comment, derivedcomment, documentclass, contentpreview'. If empty or null all fields will be returned. Example: "id,name,contentpreview,tags"
        """
        q_params = {}
        if tags is not None:
            q_params["tags"] = tags
        if documentids is not None:
            q_params["documentids"] = documentids
        if name is not None:
            q_params["name"] = name
        if createdafter is not None:
            q_params["createdafter"] = createdafter
        if createdbefore is not None:
            q_params["createdbefore"] = createdbefore
        if updatedafter is not None:
            q_params["updatedafter"] = updatedafter
        if updatedbefore is not None:
            q_params["updatedbefore"] = updatedbefore
        if documentclassids is not None:
            q_params["documentclassids"] = documentclassids
        if withoutdocumentclass is not None:
            q_params["withoutdocumentclass"] = withoutdocumentclass
        if mincharacters is not None:
            q_params["mincharacters"] = mincharacters
        if metadata is not None:
            q_params["metadata"] = metadata
        if comment is not None:
            q_params["comment"] = comment
        if sourcedoc is not None:
            q_params["sourcedoc"] = sourcedoc
        if sourcedocumentid is not None:
            q_params["sourcedocumentid"] = sourcedocumentid
        if offset is not None:
            q_params["offset"] = offset
        if limit is not None:
            q_params["limit"] = limit
        if sort is not None:
            q_params["sort"] = sort
        if fields is not None:
            q_params["fields"] = fields
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.XLSX)).execute().as_bytesio()

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
        addsourcedocument: bool = None,
    ) -> List[DocumentInformation]:
        """
        Add a reference document a.k.a. library item.
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
        if addsourcedocument is not None:
            q_params["addsourcedocument"] = addsourcedocument
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
        return response.to(DocumentInformationSchema)
    def post_json(
        self,
        body: List[Document] = None,
        detectlanguage: bool = None,
        addsourcedocument: bool = None,
    ) -> List[DocumentInformation]:
        """
        Add a reference document a.k.a. library item.
        Args:
        body (List[Document]): 
        """
        q_params = {}
        if detectlanguage is not None:
            q_params["detectlanguage"] = detectlanguage
        if addsourcedocument is not None:
            q_params["addsourcedocument"] = addsourcedocument
        response = self._session.post(
            url=self._endpoint,
            json=DocumentSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentInformationSchema)

    def patch(
        self,
        body: List[DocumentInformation]
    ) -> None:
        """
        Update metadata of multiple reference documents. Needs roles: 'Domain Admin' or 'Expert User'
        """
        return self._session.patch(
            url=self._endpoint,
            json=DocumentInformationSchema().dump(body, many=True)
        ).execute().as_none()

    def delete(
        self,
    ) -> None:
        """
        Delete all reference documents. Needs roles: 'Domain Admin' or 'Expert User'
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    