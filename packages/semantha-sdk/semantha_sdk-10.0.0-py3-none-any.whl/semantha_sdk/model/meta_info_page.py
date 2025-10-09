from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import Optional

@dataclass
class MetaInfoPage:
    """ author semantha, this is a generated class do not change manually! """
    from_: Optional[int] = None
    to: Optional[int] = None
    total: Optional[int] = None

MetaInfoPageSchema = class_schema(MetaInfoPage, base_schema=RestSchema)
