from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class DocumentMetaData:
    """ author semantha, this is a generated class do not change manually! """
    file_name: Optional[str] = None
    document_type: Optional[str] = None

DocumentMetaDataSchema = class_schema(DocumentMetaData, base_schema=RestSchema)
