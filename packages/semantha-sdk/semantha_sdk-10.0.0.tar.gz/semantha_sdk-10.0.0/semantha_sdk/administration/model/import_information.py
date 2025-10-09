from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.administration.model.import_detail import ImportDetail
from typing import List
from typing import Optional

@dataclass
class ImportInformation:
    """ author semantha, this is a generated class do not change manually! """
    status: Optional[str] = None
    message: Optional[str] = None
    details: Optional[List[ImportDetail]] = None

ImportInformationSchema = class_schema(ImportInformation, base_schema=RestSchema)
