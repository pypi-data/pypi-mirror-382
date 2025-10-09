from io import IOBase
from semantha_sdk.model.document import Document
from semantha_sdk.model.document import DocumentSchema
from semantha_sdk.model.documentmode_enum import DocumentmodeEnum
from semantha_sdk.model.type_enum import TypeEnum
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class DocumentsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documents"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/documents"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        file: IOBase = None,
        text: str = None,
        type: TypeEnum = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        withcharacters: bool = None,
        withformatinfo: bool = None,
        page: int = None,
        x: float = None,
        y: float = None,
        width: float = None,
        height: float = None,
        documentmode: DocumentmodeEnum = None,
        withparagraphtype: bool = None,
        withsentences: bool = None,
    ) -> List[Document]:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (TypeEnum): Choose the structure of a document can be 'similarity' or 'extraction'. The type depends on the Use Case you're in.
    documenttype (str): Id of the document template to use
    withareas (bool): Gives back the coordinates of sentences.
    withcontextparagraphs (bool): Gives back the context paragraphs.
    withcharacters (bool): Gives back the coordinates for each character of a sentence.
    withformatinfo (bool): Gives back aggregated formatting information of paragraphs for this document.
    page (int): Number of the page to return as image. Zero based. Only for accept=image/png
    x (float): X position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    y (float): Y position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    width (float): Width in pixel (72dpi) of the area to return as image. Only for accept=image/png
    height (float): Height in pixel (72dpi) of the area to return as image. Only for accept=image/png
    documentmode (DocumentmodeEnum): Determines to return paragraphs as rows or sentences. Only for accept=xlsx
    withparagraphtype (bool): documentmode=paragraph only and true -> text type is returned in column B. Only for accept=xlsx
        """
        q_params = {}
        if withsentences is not None:
            q_params["withsentences"] = withsentences
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "withcharacters": withcharacters,
                "withformatinfo": withformatinfo,
                "page": page,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "documentmode": documentmode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentSchema)
    def post_as_xlsx(
        self,
        file: IOBase = None,
        text: str = None,
        type: TypeEnum = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        withcharacters: bool = None,
        withformatinfo: bool = None,
        page: int = None,
        x: float = None,
        y: float = None,
        width: float = None,
        height: float = None,
        documentmode: DocumentmodeEnum = None,
        withparagraphtype: bool = None,
        withsentences: bool = None,
    ) -> IOBase:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (TypeEnum): Choose the structure of a document can be 'similarity' or 'extraction'. The type depends on the Use Case you're in.
    documenttype (str): Id of the document template to use
    withareas (bool): Gives back the coordinates of sentences.
    withcontextparagraphs (bool): Gives back the context paragraphs.
    withcharacters (bool): Gives back the coordinates for each character of a sentence.
    withformatinfo (bool): Gives back aggregated formatting information of paragraphs for this document.
    page (int): Number of the page to return as image. Zero based. Only for accept=image/png
    x (float): X position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    y (float): Y position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    width (float): Width in pixel (72dpi) of the area to return as image. Only for accept=image/png
    height (float): Height in pixel (72dpi) of the area to return as image. Only for accept=image/png
    documentmode (DocumentmodeEnum): Determines to return paragraphs as rows or sentences. Only for accept=xlsx
    withparagraphtype (bool): documentmode=paragraph only and true -> text type is returned in column B. Only for accept=xlsx
        """
        q_params = {}
        if withsentences is not None:
            q_params["withsentences"] = withsentences
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "withcharacters": withcharacters,
                "withformatinfo": withformatinfo,
                "page": page,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "documentmode": documentmode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.XLSX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()
    def post_as_docx(
        self,
        file: IOBase = None,
        text: str = None,
        type: TypeEnum = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        withcharacters: bool = None,
        withformatinfo: bool = None,
        page: int = None,
        x: float = None,
        y: float = None,
        width: float = None,
        height: float = None,
        documentmode: DocumentmodeEnum = None,
        withparagraphtype: bool = None,
        withsentences: bool = None,
    ) -> IOBase:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (TypeEnum): Choose the structure of a document can be 'similarity' or 'extraction'. The type depends on the Use Case you're in.
    documenttype (str): Id of the document template to use
    withareas (bool): Gives back the coordinates of sentences.
    withcontextparagraphs (bool): Gives back the context paragraphs.
    withcharacters (bool): Gives back the coordinates for each character of a sentence.
    withformatinfo (bool): Gives back aggregated formatting information of paragraphs for this document.
    page (int): Number of the page to return as image. Zero based. Only for accept=image/png
    x (float): X position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    y (float): Y position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    width (float): Width in pixel (72dpi) of the area to return as image. Only for accept=image/png
    height (float): Height in pixel (72dpi) of the area to return as image. Only for accept=image/png
    documentmode (DocumentmodeEnum): Determines to return paragraphs as rows or sentences. Only for accept=xlsx
    withparagraphtype (bool): documentmode=paragraph only and true -> text type is returned in column B. Only for accept=xlsx
        """
        q_params = {}
        if withsentences is not None:
            q_params["withsentences"] = withsentences
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "withcharacters": withcharacters,
                "withformatinfo": withformatinfo,
                "page": page,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "documentmode": documentmode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.DOCX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()
    def post_as_png(
        self,
        file: IOBase = None,
        text: str = None,
        type: TypeEnum = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        withcharacters: bool = None,
        withformatinfo: bool = None,
        page: int = None,
        x: float = None,
        y: float = None,
        width: float = None,
        height: float = None,
        documentmode: DocumentmodeEnum = None,
        withparagraphtype: bool = None,
        withsentences: bool = None,
    ) -> IOBase:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (TypeEnum): Choose the structure of a document can be 'similarity' or 'extraction'. The type depends on the Use Case you're in.
    documenttype (str): Id of the document template to use
    withareas (bool): Gives back the coordinates of sentences.
    withcontextparagraphs (bool): Gives back the context paragraphs.
    withcharacters (bool): Gives back the coordinates for each character of a sentence.
    withformatinfo (bool): Gives back aggregated formatting information of paragraphs for this document.
    page (int): Number of the page to return as image. Zero based. Only for accept=image/png
    x (float): X position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    y (float): Y position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    width (float): Width in pixel (72dpi) of the area to return as image. Only for accept=image/png
    height (float): Height in pixel (72dpi) of the area to return as image. Only for accept=image/png
    documentmode (DocumentmodeEnum): Determines to return paragraphs as rows or sentences. Only for accept=xlsx
    withparagraphtype (bool): documentmode=paragraph only and true -> text type is returned in column B. Only for accept=xlsx
        """
        q_params = {}
        if withsentences is not None:
            q_params["withsentences"] = withsentences
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "withcharacters": withcharacters,
                "withformatinfo": withformatinfo,
                "page": page,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "documentmode": documentmode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.PNG),
            q_params=q_params
        ).execute()
        return response.as_bytesio()
    def post_as_reqifz(
        self,
        file: IOBase = None,
        text: str = None,
        type: TypeEnum = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        withcharacters: bool = None,
        withformatinfo: bool = None,
        page: int = None,
        x: float = None,
        y: float = None,
        width: float = None,
        height: float = None,
        documentmode: DocumentmodeEnum = None,
        withparagraphtype: bool = None,
        withsentences: bool = None,
    ) -> IOBase:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (TypeEnum): Choose the structure of a document can be 'similarity' or 'extraction'. The type depends on the Use Case you're in.
    documenttype (str): Id of the document template to use
    withareas (bool): Gives back the coordinates of sentences.
    withcontextparagraphs (bool): Gives back the context paragraphs.
    withcharacters (bool): Gives back the coordinates for each character of a sentence.
    withformatinfo (bool): Gives back aggregated formatting information of paragraphs for this document.
    page (int): Number of the page to return as image. Zero based. Only for accept=image/png
    x (float): X position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    y (float): Y position in pixel (72dpi) of the area to return as image. Only for accept=image/png
    width (float): Width in pixel (72dpi) of the area to return as image. Only for accept=image/png
    height (float): Height in pixel (72dpi) of the area to return as image. Only for accept=image/png
    documentmode (DocumentmodeEnum): Determines to return paragraphs as rows or sentences. Only for accept=xlsx
    withparagraphtype (bool): documentmode=paragraph only and true -> text type is returned in column B. Only for accept=xlsx
        """
        q_params = {}
        if withsentences is not None:
            q_params["withsentences"] = withsentences
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "withcharacters": withcharacters,
                "withformatinfo": withformatinfo,
                "page": page,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "documentmode": documentmode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.REQIFZ),
            q_params=q_params
        ).execute()
        return response.as_bytesio()

    
    
    