from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.administration.model.error_field import ErrorField
from typing import List
from typing import Optional

@dataclass
class ImportDetail:
    """ author semantha, this is a generated class do not change manually! """
    name: Optional[str] = None
    file_name: Optional[str] = None
    deleted_before_import: Optional[str] = None
    import_status: Optional[str] = None
    import_error_message: Optional[str] = None
    server_errors: Optional[List[ErrorField]] = None

ImportDetailSchema = class_schema(ImportDetail, base_schema=RestSchema)
