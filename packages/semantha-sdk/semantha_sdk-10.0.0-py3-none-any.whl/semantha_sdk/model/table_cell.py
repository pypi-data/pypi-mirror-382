from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class TableCell:
    """ author semantha, this is a generated class do not change manually! """
    text: Optional[str] = None

TableCellSchema = class_schema(TableCell, base_schema=RestSchema)
