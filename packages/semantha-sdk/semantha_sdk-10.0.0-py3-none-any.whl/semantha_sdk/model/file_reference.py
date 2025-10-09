from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class FileReference:
    """ author semantha, this is a generated class do not change manually! """
    file_id: Optional[str] = None
    name: Optional[str] = None
    page_number: Optional[int] = None

FileReferenceSchema = class_schema(FileReference, base_schema=RestSchema)
