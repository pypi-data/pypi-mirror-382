from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.row import Row
from typing import List
from typing import Optional

@dataclass
class DocumentTable:
    """ author semantha, this is a generated class do not change manually! """
    rows: Optional[List[Row]] = None

DocumentTableSchema = class_schema(DocumentTable, base_schema=RestSchema)
