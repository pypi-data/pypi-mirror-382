from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.annotation_page import AnnotationPage
from semantha_sdk.model.document_table import DocumentTable
from semantha_sdk.model.page_content import PageContent
from semantha_sdk.model.paragraph import Paragraph
from typing import List
from typing import Optional

@dataclass
class Page:
    """ author semantha, this is a generated class do not change manually! """
    contents: Optional[List[PageContent]] = None
    paragraphs: Optional[List[Paragraph]] = None
    tables: Optional[List[DocumentTable]] = None
    annotation_page: Optional[AnnotationPage] = None

PageSchema = class_schema(Page, base_schema=RestSchema)
