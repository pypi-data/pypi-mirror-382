from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class DocumentNamedEntity:
    """ author semantha, this is a generated class do not change manually! """
    name: Optional[str] = None
    text: Optional[str] = None

DocumentNamedEntitySchema = class_schema(DocumentNamedEntity, base_schema=RestSchema)
