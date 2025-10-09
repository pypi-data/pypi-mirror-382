from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Link:
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    paragraph_id: Optional[str] = None

LinkSchema = class_schema(Link, base_schema=RestSchema)
