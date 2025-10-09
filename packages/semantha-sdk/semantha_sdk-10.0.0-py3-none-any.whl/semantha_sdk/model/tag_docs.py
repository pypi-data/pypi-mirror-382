from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class TagDocs:
    """ author semantha, this is a generated class do not change manually! """
    tag: Optional[str] = None
    count: Optional[int] = None

TagDocsSchema = class_schema(TagDocs, base_schema=RestSchema)
