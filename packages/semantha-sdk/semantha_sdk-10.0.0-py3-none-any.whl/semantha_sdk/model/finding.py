from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Finding:
    """ author semantha, this is a generated class do not change manually! """
    status_code: Optional[int] = None
    severity: Optional[str] = None
    message: Optional[str] = None

FindingSchema = class_schema(Finding, base_schema=RestSchema)
