from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class Version:
    """ author semantha, this is a generated class do not change manually! """
    tt: Optional[str] = None
    customer: Optional[str] = None

VersionSchema = class_schema(Version, base_schema=RestSchema)
