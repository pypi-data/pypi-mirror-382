from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.table_cell import TableCell
from typing import List
from typing import Optional

@dataclass
class Row:
    """ author semantha, this is a generated class do not change manually! """
    cells: Optional[List[TableCell]] = None

RowSchema = class_schema(Row, base_schema=RestSchema)
