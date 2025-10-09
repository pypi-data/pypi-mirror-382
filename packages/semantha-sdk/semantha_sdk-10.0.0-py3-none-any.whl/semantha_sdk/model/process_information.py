from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.version import Version
from typing import Optional

@dataclass
class ProcessInformation:
    """ author semantha, this is a generated class do not change manually! """
    created: Optional[str] = None
    edited: Optional[str] = None
    version: Optional[Version] = None

ProcessInformationSchema = class_schema(ProcessInformation, base_schema=RestSchema)
