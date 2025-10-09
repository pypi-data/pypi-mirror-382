from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class FormatInformation:
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[int] = None
    text_type: Optional[str] = None
    fontsize: Optional[int] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    count: Optional[int] = None
    target_text_type: Optional[str] = None

FormatInformationSchema = class_schema(FormatInformation, base_schema=RestSchema)
