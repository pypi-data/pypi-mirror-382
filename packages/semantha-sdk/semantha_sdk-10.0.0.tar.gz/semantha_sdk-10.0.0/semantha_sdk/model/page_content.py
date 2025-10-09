from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.paragraph import Paragraph
from typing import List
from typing import Optional

@dataclass
class PageContent:
    """ author semantha, this is a generated class do not change manually! """
    paragraphs: Optional[List[Paragraph]] = None

PageContentSchema = class_schema(PageContent, base_schema=RestSchema)
